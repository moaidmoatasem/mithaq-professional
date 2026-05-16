import json
import logging
import socket
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

class SIEMForwarder:
    """
    Enterprise SIEM integration for Cherenkov.
    Supports Syslog (CEF) and Splunk HEC.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", False)
        self.mode = self.config.get("mode", "syslog") # syslog or splunk
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 514)
        self.token = self.config.get("token", "") # For Splunk HEC
        
    async def forward_finding(self, finding: Dict[str, Any], scan_metadata: Dict[str, Any]) -> bool:
        if not self.enabled:
            return False
            
        payload = {
            "event": "finding_discovered",
            "scanner": finding.get("scanner"),
            "severity": finding.get("severity"),
            "title": finding.get("title"),
            "target": scan_metadata.get("target"),
            "scan_id": scan_metadata.get("scan_id"),
            "timestamp": scan_metadata.get("timestamp")
        }
        
        try:
            if self.mode == "syslog":
                return await self._send_syslog(payload)
            elif self.mode == "splunk":
                return await self._send_splunk(payload)
            return False
        except Exception as e:
            logger.error(f"SIEM forwarding failed: {e}")
            return False
            
    async def _send_syslog(self, payload: Dict[str, Any]) -> bool:
        # CEF Format: CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]
        cef = f"CEF:0|Cherenkov|SecurityPlatform|1.1.0|FINDING|{payload['title']}|{payload['severity']}|target={payload['target']} scan_id={payload['scan_id']}"
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(cef.encode(), (self.host, self.port))
            return True
        finally:
            sock.close()
            
    async def _send_splunk(self, payload: Dict[str, Any]) -> bool:
        async with httpx.AsyncClient(verify=False) as client:
            headers = {"Authorization": f"Splunk {self.token}"}
            url = f"https://{self.host}:{self.port}/services/collector/event"
            r = await client.post(url, json={"event": payload}, headers=headers)
            return r.status_code == 200
