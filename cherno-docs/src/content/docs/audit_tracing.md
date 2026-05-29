# Audit Tracing

All scans are now traced using the `save_trace` function in `database.py`.
It logs a `scan_trace` event to the `audit_log` table containing a `trace_hash`.

Traces are cryptographically anchored and RFC 3161 timestamped via `freetsa.org` to ensure forensic immutability (MEISSNER compliant). The output includes `tsa_status`, `tsr_b64`, `signed_at`, and `standard` fields to verify timestamp integrity. Network failures gracefully degrade to `tsa_status=unavailable` without blocking execution.
