# Security Policy

> *CHERENKOV is a sovereign security platform. Its own security posture must be beyond reproach.*

## Reporting Vulnerabilities

If you discover a security vulnerability in CHERENKOV, please report it confidentially:

- **Email**: info@cherenkov-security.com
- **Response Window**: Within 24 hours (acknowledgment). Resolution target within 7 days.
- **PGP Key**: Available at `https://cherenkov-security.com/pgp-key.asc`

## Disclosure Process

1. **Report**: Send details to info@cherenkov-security.com. Include steps to reproduce, affected versions, and potential impact.
2. **Triage**: Maintainers will acknowledge receipt within 24 hours and begin triage.
3. **Embargo**: A coordinated disclosure date will be agreed. Default embargo: 90 days.
4. **Fix**: A patch is developed, tested through the validation pipeline, and deployed to the release branch.
5. **Disclosure**: Published as a security advisory on GitHub with CVE assignment.

## What We Investigate

| Scope | Covered |
|---|---|
| Core platform (`packages/cherenkov/core/`) | ✅ |
| API layer (`packages/cherenkov/api/`) | ✅ |
| Deployment infra (`deploy/`) | ✅ |
| Scanner engine | ✅ |
| Third-party integrations | ✅ (when impact is to CHERENKOV users) |
| AI agent output quality | ❌ (use `security-advisory` label for critical misbehaviour) |

## Bug Bounty

CHERENKOV does not currently operate a paid bug bounty program. Contributors who report valid, critical findings will receive:

- Public acknowledgment in release notes
- Direct credit in the security advisory
- Priority review of their first PR

## Safe Harbour

We pledge not to pursue legal action against researchers who:

- Report vulnerabilities in good faith
- Follow the disclosure process
- Do not access or exfiltrate user data
- Do not disrupt production systems

## Shred Receipt Protocol

After a vulnerability is resolved, all related test data, PoC artifacts, and communication logs must be cryptographically erased. A Shred Receipt (SHA-256 signed JSON) is generated as proof of erasure.

---

*Last updated: May 2026*