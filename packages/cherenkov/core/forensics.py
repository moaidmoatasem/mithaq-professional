"""
Forensic signing: SHA-256 content hash + RFC 3161 trusted timestamp.

Air-gap behaviour: TSA call is best-effort. If the network is unavailable
(expected in MEISSNER-isolated nodes), tsa_status is set to "unavailable"
and the SHA-256 anchor alone is stored. The hash is still cryptographically
binding — the TSA token adds a trusted wall-clock proof for legal contexts.
"""

import base64
import hashlib
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

_TSA_URL = "https://freetsa.org/tsr"
_TSA_TIMEOUT = 5.0


# ── DER helpers ───────────────────────────────────────────────────────────────

def _encode_length(n: int) -> bytes:
    if n < 0x80:
        return bytes([n])
    lb = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(lb)]) + lb


def _tlv(tag: int, value: bytes) -> bytes:
    return bytes([tag]) + _encode_length(len(value)) + value


def _build_tsa_request(message_hash: bytes) -> bytes:
    """Build a minimal RFC 3161 TimeStampReq DER for SHA-256."""
    # AlgorithmIdentifier ::= SEQUENCE { OID sha-256, NULL }
    algo_id = bytes.fromhex("300d06096086480165030402010500")
    msg_imprint = _tlv(0x30, algo_id + _tlv(0x04, message_hash))

    # Nonce INTEGER — prefix 0x00 if high bit set (ASN.1 positive integer rule)
    raw = os.urandom(8)
    nonce_val = (b"\x00" + raw) if (raw[0] & 0x80) else raw
    nonce = _tlv(0x02, nonce_val)

    cert_req = bytes.fromhex("0101ff")  # BOOLEAN TRUE — ask TSA to include its cert
    version = bytes.fromhex("020101")   # INTEGER 1

    return _tlv(0x30, version + msg_imprint + nonce + cert_req)


# ── Public API ────────────────────────────────────────────────────────────────

def sign_trace(findings_payload: str) -> Dict[str, str]:
    """
    Return a cryptographic_anchor dict for CherenkovTrace.

    Always produces a SHA-256 digest of *findings_payload*.
    Attempts an RFC 3161 timestamp from freetsa.org; falls back gracefully
    when the node is air-gapped (MEISSNER-isolated).
    """
    digest = hashlib.sha256(findings_payload.encode()).hexdigest()
    anchor: Dict[str, str] = {"sha256": digest, "tsa_status": "skipped"}

    try:
        import httpx  # already a project dependency

        tsa_req = _build_tsa_request(bytes.fromhex(digest))
        resp = httpx.post(
            _TSA_URL,
            content=tsa_req,
            headers={"Content-Type": "application/timestamp-query"},
            timeout=_TSA_TIMEOUT,
        )
        if resp.status_code == 200:
            anchor["tsa_token"] = base64.b64encode(resp.content).decode()
            anchor["tsa_server"] = _TSA_URL
            anchor["tsa_status"] = "ok"
            logger.info("RFC 3161 timestamp obtained from %s", _TSA_URL)
        else:
            anchor["tsa_status"] = f"http_{resp.status_code}"
            logger.warning("TSA returned HTTP %s", resp.status_code)
    except Exception as exc:
        logger.debug("TSA unavailable (air-gap expected): %s", exc)
        anchor["tsa_status"] = "unavailable"

    return anchor
