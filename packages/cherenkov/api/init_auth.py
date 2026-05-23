import os
import secrets

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

load_dotenv()

API_KEY_NAME = "X-Cherenkov-Token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    expected_key = os.getenv("CHERENKOV_API_KEY")
    if not expected_key:
        raise HTTPException(status_code=500, detail="C2 Hub authentication not configured.")
    if not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(status_code=403, detail="MEISSNER protocol: Access denied.")
    return api_key
