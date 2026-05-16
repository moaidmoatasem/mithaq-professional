from cherenkov.core.ablation.bridge import AblationBridge, DropReason, SanitizationError


def test_sanitize_success():
    bridge = AblationBridge()
    finding = {"issue": "SQLi found"}
    result = bridge.sanitize(finding)
    assert result.sanitized_payload == finding
    assert result.redaction_count == 0


def test_sanitize_redacts_credentials():
    bridge = AblationBridge()
    finding = {"key": "AKIAIOSFODNN7EXAMPLE"}
    result = bridge.sanitize(finding)
    assert result.sanitized_payload["key"] == "[AWS_KEY_REDACTED]"
    assert result.redaction_count == 1


def test_sanitize_rejects_binary():
    bridge = AblationBridge()
    finding = {"data": b"binary"}
    try:
        bridge.sanitize(finding)
        raise AssertionError()
    except SanitizationError as e:
        assert e.reason == DropReason.BINARY_CONTENT
