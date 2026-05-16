# Task: Issue #175 — HITL Approval Gate

**Split into two independent branches:**

| Half | Branch | Agent |
|---|---|---|
| Backend | `feat/175-hitl-backend` | Jules / OpenCode / @claude |
| Frontend | `feat/175-hitl-frontend` | Antigravity / any frontend agent |

Both PRs must contain `Closes #175` — GitHub will close the issue when either merges.

---

## Backend half

**Context files:**
```
packages/cherenkov/api/main.py
packages/cherenkov/core/storage/database.py
packages/cherenkov/core/base_scanner.py  ← Severity enum
```

### Schema

```python
class FindingApproval(BaseModel):
    finding_id: str
    severity: str          # CRITICAL | HIGH
    scanner: str
    title: str
    description: str
    status: Literal["pending", "approved", "rejected"] = "pending"
    operator_id: Optional[str] = None
    approved_at: Optional[str] = None
```

### SQLite table (in database.py)
```sql
CREATE TABLE IF NOT EXISTS findings_pending (
    id TEXT PRIMARY KEY,
    severity TEXT, scanner TEXT, title TEXT, description TEXT,
    status TEXT DEFAULT 'pending',
    operator_id TEXT, approved_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
)
```

### Endpoints (add to v1 router in main.py)
```
POST /api/v1/findings/{id}/approve
POST /api/v1/findings/{id}/reject
GET  /api/v1/findings/pending
```

### Hook into scan flow
In `_run_scan()`: for any `finding.severity in (CRITICAL, HIGH)` → insert into `findings_pending` + broadcast `{"type":"finding_discovered", "finding_id":..., "severity":...}`.

### Verify
```bash
ruff format packages/ && pytest tests/ -m "not (integration or ai_generated)" --tb=short
```

---

## Frontend half

**Context files:**
```
packages/cherenkov/web/src/lib/api.ts          ← add fetch helpers
packages/cherenkov/web/src/hooks/useMetrics.ts ← add usePendingApprovals hook
packages/cherenkov/web/src/components/organisms/ForensicHeader.tsx ← add badge
```

### Add to api.ts
```typescript
export async function fetchPendingApprovals(): Promise<FindingApproval[]>
export async function approveFinding(id: string): Promise<void>
export async function rejectFinding(id: string): Promise<void>
```

### New hook in useMetrics.ts
```typescript
export function usePendingApprovals(intervalMs = 5000) { ... }
```

### New organism: `PendingApprovalsPanel.tsx`
- List of pending findings with severity badge
- Approve / Reject `CyberButton` per finding
- Empty state: "No pending approvals"

### ForensicHeader badge
- Count from `useLiveEvents` `finding_discovered` event
- Red pulse dot when count > 0

### Verify
```bash
cd packages/cherenkov/web && npm run lint && npx vite build
```
