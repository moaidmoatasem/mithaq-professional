from mithaq.siyaada.redactor import DataRedactor, RedactionLevel

# Test data with secrets
test_data = {
    "app_name": "BankingApp",
    "api_key": "sk_live_1234567890abcdefghijklmnop",
    "database_url": "mongodb://admin:password123@localhost:27017/banking",
    "user_email": "test@example.com",
    "config_path": "/home/user/secrets/.env",
    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
    "metadata": {
        "platform": "Android",
        "version": "1.2.3"
    }
}

print("Testing Data Redaction Layer\n")
print("Original Data:")
print(test_data)
print("\n" + "="*60 + "\n")

# Create redactor
redactor = DataRedactor(level=RedactionLevel.MODERATE)

# Redact data
result = redactor.redact_dict(test_data)

print("Sanitized Data:")
print(result.sanitized_data)
print("\n" + "="*60 + "\n")

print(f"Redacted Fields: {', '.join(result.redacted_fields)}")
print(f"Hash Signature: {result.hash_signature}")
print(f"Safe for Cloud: {result.is_safe}")

if result.warnings:
    print(f"Warnings: {', '.join(result.warnings)}")

# Test breadcrumb creation
print("\n" + "="*60 + "\n")
print("Cloud Breadcrumb (Metadata Only):")
breadcrumb = redactor.create_breadcrumb(test_data, metadata_only=True)
print(breadcrumb)

