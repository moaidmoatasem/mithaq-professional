# Validated Scanners

CHERENKOV ships with a growing library of validated scanners. These scanners have been tested against known targets and produce TOKAMAK-verifiable results.

## Current Inventory

| Scanner | File | Category | CWE | Status |
|---|---|---|---|---|---|
| HTTP Security Headers | header_scanner.py | Web | CWE-693, CWE-16 | ✅ Validated |
| Security Header Analysis | security_headers.py | Web | CWE-693 | ✅ Validated |
| Dangerous HTTP Methods | http_methods.py | Web | CWE-749 | ✅ Validated |
| TLS Version Detection | tls_detection.py | Web/TLS | CWE-326, CWE-327 | ✅ Validated |
| Unified Web Scanner | unified_scanner.py | Web | Multiple | ✅ Validated |
| Local Path Traversal Scanner | local_path_traversal_scanner.py | Web | CWE-22 | ✅ Validated |
| Static XXE Scanner | static_xxe_scanner.py | Web/XML | CWE-611, CWE-776 | ✅ Validated |
| Component CVE Scanner | component_cve_scanner.py | Dependency | Multiple | ✅ Validated |
| Static File Upload Scanner | static_file_upload_scanner.py | Web | CWE-434 | ✅ Validated |
| Severity Classifier Scanner | severity_classifier_scanner.py | Web/Infra | CWE-200, CWE-1104 | ✅ Validated |

## Target: 20 Validated Scanners (Phase 3)

The Phase 3 roadmap targets 20 validated scanners covering OWASP Top 10, API, and infrastructure categories. Mobile (Android/iOS) scanners are planned for Phase 4.
