# 🗄️ CHERENKOV — DB Schema Evolution & Record History

This file tracks the schemas, structural migrations, and runtime record buildup history across the entire Cherenkov system.

---

## 🏗️ 1. Active Database Architecture

Cherenkov employs a dual-database architecture optimized for high-performance security operations and absolute record immutability. Both databases utilize **SQLite with Write-Ahead Logging (WAL)** to enable parallel reads and safe concurrent writing.

```
~/.cherenkov/
├── results.db       ← Operations Database (scans, findings, users, circuit breaker state)
└── reasoning.db     ← Reasoning Trace Database (immutable agent cognitive step records)
```

---

## 📊 2. Operations Database Schema (`results.db`)

### A. Table: `scans`
Stores high-level data representing executed scanner tasks.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Auto-incremented local identifier |
| `scan_id` | `TEXT` | `NOT NULL UNIQUE` | Unique UUID string for the scan session |
| `target` | `TEXT` | `NOT NULL` | The target URL or IP being scanned |
| `started_at` | `TEXT` | `NOT NULL` | Timestamp scan was initiated |
| `finished_at` | `TEXT` | | Timestamp scan was finalized |
| `status` | `TEXT` | `NOT NULL DEFAULT 'running'` | Status (`running`, `completed`, `failed`) |
| `meta` | `TEXT` | `NOT NULL DEFAULT '{}'` | JSON metadata blob for configuration |

### B. Table: `findings_pending`
Stores findings awaiting Human-in-the-Loop (HITL) triage.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Auto-incremented local identifier |
| `finding_id` | `TEXT` | `NOT NULL UNIQUE` | Unique finding UUID |
| `severity` | `TEXT` | `NOT NULL` | Severity status (`critical`, `high`, `medium`, `low`) |
| `scanner` | `TEXT` | `NOT NULL` | Source scanner name |
| `title` | `TEXT` | `NOT NULL` | Short title of the vulnerability |
| `description` | `TEXT` | `NOT NULL` | Detailed vulnerability explanation |
| `status` | `TEXT` | `NOT NULL DEFAULT 'pending'` | Status (`pending`, `approved`, `rejected`) |
| `approved_at` | `TEXT` | | Timestamp of HITL action |
| `scan_id` | `TEXT` | | Foreign scan UUID |

### C. Table: `users`
System RBAC user roles.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Local ID |
| `username` | `TEXT` | `NOT NULL UNIQUE` | Login username |
| `password` | `TEXT` | `NOT NULL` | Argon2/Bcrypt password hash |
| `role` | `INTEGER` | `NOT NULL DEFAULT 1` | Role permissions level (1 = Auditor, 2 = Admin) |

### D. Table: `audit_log`
Immutable system events recorded with cryptographic PoC execution signatures.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Local ID |
| `timestamp` | `TEXT` | `NOT NULL` | Event timestamp |
| `event_type` | `TEXT` | `NOT NULL` | Type (`scan_start`, `hitl_action`, `poc_sign`) |
| `user_id` | `TEXT` | | Acting user UUID or username |
| `details` | `TEXT` | `NOT NULL DEFAULT '{}'` | JSON payload metadata |
| `trace_hash` | `TEXT` | `NOT NULL` | Cryptographic PoC SHA-256 signature |

### E. Table: `circuit_breaker_state`
Controls circuit states for external/LLM calls.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `key` | `TEXT` | `PRIMARY KEY` | Breaker target identifier |
| `state` | `TEXT` | `NOT NULL DEFAULT 'closed'` | Breaker state (`closed`, `open`, `half-open`) |
| `failure_count`| `INTEGER` | `NOT NULL DEFAULT 0` | Current threshold counter |
| `last_failure_time`| `REAL` | | Last failure timestamp float |
| `updated_at` | `TEXT` | `NOT NULL` | Last update ISO timestamp |

---

## 🧠 3. Cognitive Reasoning Schema (`reasoning.db`)

### Table: `reasoning_traces`
Records atomic decision-making steps taken by AI Agents.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `trace_id` | `TEXT` | `PRIMARY KEY` | Trace step UUID |
| `agent_id` | `TEXT` | `NOT NULL` | UUID of executing agent instance |
| `agent_role` | `TEXT` | `NOT NULL` | Persona role (e.g. `tester`, `pm`) |
| `session_id` | `TEXT` | `NOT NULL` | Mapped chat/scan session UUID |
| `step_index` | `INT` | `NOT NULL` | Chronological step order number |
| `step_type` | `TEXT` | `NOT NULL` | Step nature (`thought`, `action`, `observation`) |
| `input_summary`| `TEXT` | `NOT NULL` | Redacted input summary |
| `output_summary`| `TEXT` | `NOT NULL` | Redacted output summary |
| `reasoning` | `TEXT` | `NOT NULL` | Detailed internal agent deliberation content |
| `confidence` | `REAL` | | Self-reported agent confidence |
| `model_backend`| `TEXT` | | LLM Model description |
| `latency_ms` | `INT` | | Compute duration millisecond count |
| `tool_name` | `TEXT` | | MCP or system tool invoked (if any) |
| `tool_args_hash`| `TEXT` | | Hash signature of parameters for verification |
| `sha256_anchor`| `TEXT` | `NOT NULL` | SHA-256 hash anchoring the previous trace step |
| `timestamp` | `TEXT` | `NOT NULL` | Trace recording timestamp |

---

## 📈 4. Data Buildup Workflow

The system guarantees clear chronological state progression when a scan runs:

```
[Start Scan] 
     │ 
     ▼
1. Create 'scans' record (status = running)
     │
     ▼
2. Scanners run in air-gapped sandboxes (TOKAMAK)
     │
     ▼
3. For each vulnerability found:
   Create 'findings_pending' record (status = pending)
     │
     ▼
4. User clicks Approve/Reject on React Portal:
   Update 'findings_pending' record (status = approved/rejected)
   Write 'audit_log' entry signed with PoC 'trace_hash'
     │
     ▼
5. Update 'scans' record (status = completed, meta contains stats)
```

---

## 🛠️ 5. Migrations & Schema Alterations History

This section tracks migrations. Do not alter schemas without registering here first.

- **2026-05-20 (Jules)**: Split `findings` into `findings_pending` to support HITL workflows. Registered indexes `idx_findings_pending_status` and `idx_scans_started`.
- **2026-05-22 (Claude)**: Integrated SQLite WAL configuration inside `database.py` and `reasoning_store.py` (`PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;`).
