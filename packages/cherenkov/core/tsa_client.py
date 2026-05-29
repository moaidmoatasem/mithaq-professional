import base64
import os
import logging
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _encode_length(n: int) -> bytes:
    if n < 0x80:
        return bytes([n])
    lb = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(lb)]) + lb


def _tlv(tag: int, value: bytes) -> bytes:
    return bytes([tag]) + _encode_length(len(value)) + value


def _build_tsa_request(message_hash: bytes) -> bytes:
    """Build a minimal RFC 3161 TimeStampReq DER for SHA-256."""
    algo_id = bytes.fromhex("300d06096086480165030402010500")
    msg_imprint = _tlv(0x30, algo_id + _tlv(0x04, message_hash))
    raw = os.urandom(8)
    nonce_val = (b"\x00" + raw) if (raw[0] & 0x80) else raw
    nonce = _tlv(0x02, nonce_val)
    cert_req = bytes.fromhex("0101ff")
    version = bytes.fromhex("020101")
    return _tlv(0x30, version + msg_imprint + nonce + cert_req)


async def get_timestamp(trace_hash: str) -> dict:
    """
    Attempts to get an RFC 3161 timestamp for a SHA-256 hash from freetsa.org.
    Returns a dictionary with the timestamping metadata.
    """
    digest_bytes = bytes.fromhex(trace_hash)
    tsa_req = _build_tsa_request(digest_bytes)
    now = datetime.now(timezone.utc).isoformat()

    result = {"tsa_status": "unavailable", "signed_at": now, "standard": "RFC 3161"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://freetsa.org/tsr",
                content=tsa_req,
                headers={"Content-Type": "application/timestamp-query"},
                timeout=5.0,
            )
            if resp.status_code == 200:
                result["tsr_b64"] = base64.b64encode(resp.content).decode()
                result["tsa_status"] = "timestamped"
    except Exception as exc:
        # Fall back to unavailable on network failure (air-gap)
        logger.debug("TSA unavailable (air-gap expected): %s", exc)

    return result
