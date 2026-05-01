"""
Burhan Payload Tester - Deterministic exploit verification
"""
import requests
from typing import Dict, Optional

def test_sql_injection(endpoint: str, payload: str = "' OR '1'='1") -> Dict:
    """
    Test single SQL injection point
    Returns proof of exploitation
    """
    try:
        # Test payload
        response = requests.get(endpoint, params={'q': payload}, timeout=5)
        
        # Detection heuristics
        sql_errors = [
            'SQL syntax',
            'mysql_fetch',
            'ORA-',
            'postgresql',
            'sqlite_'
        ]
        
        is_vulnerable = any(err in response.text for err in sql_errors)
        
        return {
            'endpoint': endpoint,
            'payload': payload,
            'vulnerable': is_vulnerable,
            'status_code': response.status_code,
            'evidence': response.text[:500] if is_vulnerable else None,
            'burhan_proof': 'DETERMINISTIC' if is_vulnerable else 'SAFE'
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'vulnerable': False,
            'error': str(e),
            'burhan_proof': 'ERROR'
        }
