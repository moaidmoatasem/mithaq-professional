# ABLATION (Redaction)

ABLATION is the data redaction engine. In hybrid configurations where cloud AI processing is required, all data is forced through ABLATION, which strips PII, credentials, and proprietary code before egress is permitted.

## What ABLATION Removes

- Email addresses, phone numbers, government IDs
- API keys, tokens, passwords
- Proprietary source code snippets
- Internal hostnames and IPs
- Customer data

## Design

- Fails-closed on error — if redaction cannot be verified, data is not sent
- Pattern-based detection with regex and ML-based PII identification
- Configurable allow/deny lists for domain-specific terms
