# Audit Tracing

All scans are now traced using the `save_trace` function in `database.py`.
It logs a `scan_trace` event to the `audit_log` table containing a `trace_hash`.
