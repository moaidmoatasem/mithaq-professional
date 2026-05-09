import pytest

from cherenkov.core.ablation.sanitizer import AblationSanitizer, SanitizedPayload

# Test data with secrets
TEST_DATA = {
    "app_name": "SecureApp",
    "api_key": "sk_live_1234567890abcdefghijklmnop",
    "database_url": "postgresql://admin:password123@localhost:5432/db",
    "public_info": "This is safe",
}

SECRET_KEY = b"super_secret_test_key_for_hmac"


def test_sanitizer_initialization():
    sanitizer = AblationSanitizer(secret_key=SECRET_KEY)
    assert sanitizer.secret_key == SECRET_KEY

    with pytest.raises(ValueError, match="Secret key is required"):
        AblationSanitizer(secret_key=b"")


def test_sanitize_and_sign():
    sanitizer = AblationSanitizer(secret_key=SECRET_KEY)
    payload = sanitizer.sanitize_and_sign(TEST_DATA)

    assert isinstance(payload, SanitizedPayload)
    assert payload.is_safe is True

    # Check that secrets were redacted
    assert "sk_live" not in payload.sanitized_data["api_key"]
    assert "password123" not in payload.sanitized_data["database_url"]

    # Check that safe data remains
    assert payload.sanitized_data["public_info"] == "This is safe"

    # Check signature is present
    assert payload.hmac_signature is not None
    assert len(payload.hmac_signature) == 64  # SHA256 hex digest length


def test_verify_signature_success():
    sanitizer = AblationSanitizer(secret_key=SECRET_KEY)
    payload = sanitizer.sanitize_and_sign(TEST_DATA)

    # Verification should succeed on the unmodified payload
    assert sanitizer.verify_signature(payload) is True


def test_verify_signature_failure_tampered_data():
    sanitizer = AblationSanitizer(secret_key=SECRET_KEY)
    payload = sanitizer.sanitize_and_sign(TEST_DATA)

    # Tamper with the data
    payload.sanitized_data["public_info"] = "Tampered info"

    # Verification should now fail
    assert sanitizer.verify_signature(payload) is False


def test_verify_signature_failure_wrong_key():
    sanitizer1 = AblationSanitizer(secret_key=SECRET_KEY)
    payload = sanitizer1.sanitize_and_sign(TEST_DATA)

    # Verify with a different key
    sanitizer2 = AblationSanitizer(secret_key=b"different_key")
    assert sanitizer2.verify_signature(payload) is False
