# mithaq — Pre-Mortem Report
# Date: November 2026 (6 months from now)
# Classification: Honest
# Method: Prospective hindsight — assume failure, identify causes

"We launched in September 2026. By November it was clear mithaq had stalled.
GitHub: 43 stars. Zero paying users. The code runs but nobody believes it.
Here is exactly why it failed, and what we should have done."

---

## FAILURE #1: The Planning Trap (The most likely killer)

**What happened:**
We spent May–July 2026 producing eleven planning documents, five architecture
diagrams, three consolidated plans, a premortem, and a governance policy.
Claude Code ran 47 sessions. The siyaada.py file was rewritten four times.
At the end of Phase 1, the repository had 127 documentation files and 3
working scanners — the same 3 scanners from April.

**The signal we missed:**
Every session in this conversation was longer than the previous one.
When planning sessions get longer, execution has stopped.
The governance PDFs (GOV-01) were written before the code they govern existed.

**Root cause:**
Planning felt like progress. It was not progress. It was risk avoidance.
The real risk — "what if we build it and nobody uses it" — was deferred
by producing more documentation.

**What would have prevented it:**
A hard rule: no new planning document until the previous phase's code
is committed, tested, and passing CI. The ratio should be 10:1 — ten
commits for every planning session.

---

## FAILURE #2: Siyaada Drop Rate Destroyed Credibility

**What happened:**
At the Cairo pilot (September 2026), Siyaada's fail-closed logic dropped
68% of findings from the first real-world scan. The senior CBE engineer
looked at the report, saw 2 findings from what should have been a
high-surface web application, and said "this tool is broken."

It was not broken. The regex patterns were too aggressive. Stack traces
containing `/home/username/project/` were dropped entirely because the
path redaction pattern matched too broadly. Internal IP ranges in error
messages were dropped. Log files containing mixed PII and technical
evidence were dropped wholesale.

The customer saw a 30% finding rate and called it a false-negative machine.

**What would have prevented it:**
Siyaada telemetry in production from day one. If we had been watching
drop_rate in staging against real-world-like payloads (not just DVWA),
we would have seen 68% drop before the pilot. The governance documents
defined this metric. We never wired it to an alert.

The specific fix: "partial redaction fallback" — redact the identifier,
keep the structural evidence, rather than dropping the entire payload.

---

## FAILURE #3: Burhan's 30-Second Timeout Was Too Short for Mobile

**What happened:**
Every APK scan timed out the Burhan validation step. Android emulators
in Docker take 45–90 seconds to boot. The watchdog (correctly) killed
the container after 30 seconds every time. Every mobile finding came back
as PROBABLE, routed to human review. The human review queue had 847 items
by week 3 of the pilot. Nobody processed them.

The 30-second limit was correct for web PoCs. It was wrong for mobile.

**What would have prevented it:**
Two timeout constants, not one: `WEB_POC_TIMEOUT = 30`, `MOBILE_POC_TIMEOUT = 120`.
The sandbox profiles already knew which surface was running. The timeout
should have been profile-aware from the start.

---

## FAILURE #4: The Dev Crew Generated, Nobody Validated

**What happened:**
The scanner_generator.py tool worked. By June 2026, the dev crew had
generated 89 scanner candidates in candidates/. The validation gate
existed. Nobody ran it. Weeks went by. The candidates/ directory grew.

The 5-step validation gate assumed DVWA was running. DVWA was not running
unless someone explicitly started it. There was no automation that said
"start DVWA, run the gate, generate a report." It was a manual process
that required knowing to do it.

We had 89 candidates and 3 validated scanners at the community launch.

**What would have prevented it:**
A GitHub Actions workflow that runs nightly:
1. `docker-compose up dvwa webgoat -d`
2. `mithaq-dev validate-all-candidates`
3. Opens PRs for any candidate that passes all 5 steps
4. Comments on failing candidates with specific step failures

The validation gate needed to be autonomous, not a manual task.

---

## FAILURE #5: Context Window Collapse in Claude Code

**What happened:**
Claude Code sessions regularly hit the context limit mid-execution.
A session would start Phase 2, create BaseScanner, start the Registry,
hit the limit, and stop. The next session would re-read CLAUDE.md and
sometimes re-create files that already existed with slightly different
implementations. By July, there were three versions of engine.py
across different branches.

The CLAUDE.md file grew to 847 lines because we kept adding to it
without pruning. It was so large that reading it consumed a third
of the context budget before any work started.

**What would have prevented it:**
CLAUDE.md must stay under 120 lines. Hard limit. Every update requires
deleting something. The compressed version we have now is right.

Phase-specific sessions with hard scope limits:
- Session A: "Only fix the 6 items in BROKEN RIGHT NOW. Nothing else."
- Session B: "Only create src/mithaq/core/base_scanner.py and registry.py."
Never compound phases in one session.

---

## FAILURE #6: We Launched to HN Before Phase 3 Was Real

**What happened:**
On September 15, 2026, someone posted mithaq to Hacker News.
Not us — a community member who found it on GitHub.

The top comment was:
"I cloned this and ran `mithaq scan https://example.com`. It checks
3 headers and tells me if I have HTTPS. This README says 132 scanners.
That's just not true."

Second comment: "The README says 'production-ready'. There are open
CVEs in their own tool's dependencies."

The post got 147 upvotes and the comment thread was 43 replies long.
Every reply was a variant of "misleading" or "credibility gap."

We never recovered from that HN thread. The security community has a
long memory. When we actually launched with 50 validated scanners in
December 2026, the response was "didn't this get torn apart on HN?"

**What would have prevented it:**
Not a content problem. A timing problem. The "never publish before
Phase 3" rule needed to include protecting the GitHub repo from
public discovery during the build phase. Either private repo until
Phase 3, or a much more conservative README that matches reality.

---

## FAILURE #7: Single Developer Burnout at Week 23

**What happened:**
Phase 4 started. Mobile surface. APKTool, Androguard, Frida, Docker
Android emulators. The complexity jumped by an order of magnitude.
The developer (Moayed) had been working 20-hour weeks for 5 months.

Week 23: no commits. Week 24: no commits. Week 25: a commit that
deleted 400 lines and added 40. The project went into maintenance mode.

**What would have prevented it:**
Earlier community contribution. The CONTRIBUTING.md was not written
until Phase 3. The "good first issues" were not labeled until week 16.
If we had had 2 contributors validating scanners by week 10, the
Phase 4 load would not have fallen entirely on one person.

Also: the 41-week timeline with no buffer. A 20% schedule buffer
(48 weeks) would have absorbed the natural slowdowns.

---

## FAILURE #8: The Governance Documents Were Not Wired to Code

**What happened:**
GOV-01 defined: DoD 5220.22-M shredding every 72 hours, LUKS-encrypted
vault, PAM dual-approval, immutable syslog, iptables egress deny.

None of this existed in code. GOV-01 was produced in May 2026. The
code it governed was still a Flask web app. The document was written
for a system that did not exist yet, in the voice of a system that
was already deployed.

When the CBE auditor asked to see the LUKS volume configuration,
there was nothing to show. When they asked for the cron job that
ran DoD shredding, there was nothing to show.

**What would have prevented it:**
Governance documents must be written AFTER the code they govern
exists, not before. GOV-01 should have been written during Phase 5
(enterprise), not during Phase 1 planning.

Exception: the data classification tiers (Tier 1/2/3) were genuinely
useful early — they informed the Siyaada architecture. But the
operational controls (cron jobs, LUKS, PAM) should wait until
the infrastructure they describe exists.

---

## FAILURE #9: The Dual-Brain Was Never Actually Dual

**What happened:**
In October 2026, a security researcher tested mithaq's "zero cloud
exposure" claim. She ran mithaq with network monitoring. She found
that the FastAPI server, when responding to scan results, sometimes
cached intermediate LLM outputs to a temp file that was accessible
via a path traversal in the API itself.

Not a Siyaada failure. A different failure: the API layer had no
output validation, and the "dual-brain" routing was conceptual —
in the actual code, Al-Muhandis and Al-Munafeedh were not separate
processes or containers. They were two functions calling the same
Ollama endpoint in the same process. There was no enforced separation.

**What would have prevented it:**
Al-Muhandis and Al-Munafeedh must be separate processes, not
separate functions. The separation must be enforced at the OS level
(separate containers, separate users, explicit IPC), not just at
the code level.

---

## FAILURE #10: Token Costs Hit $400/Month at Scale

**What happened:**
The first enterprise pilot ran 2,000 scans in a week.
Token costs for the AI triage layer: $0.009 × 2,000 = $18/week.
Acceptable. But the enterprise customer wanted real-time triage
on every scan, and their Ollama model was unavailable, so every
call fell through to Gemini Flash.

Gemini Flash pricing was different from what was estimated.
The 5-minute cache TTL was not enabled because the deployment
engineer did not know to set it. Total cost for the week: $400.

The customer had been told "effectively $0 infrastructure."

**What would have prevented it:**
The model router must enforce the cache_control headers by default,
not optionally. The cost estimate must be surfaced to users in the
CLI: "Estimated cost for this scan: $0.009 (Gemini) / $0.000 (local)."
Every model router call must log which backend was used and why.

---

## THE PREMORTEM SUMMARY TABLE

| Failure | Probability | Impact | Preventable | Prevention |
|---|---|---|---|---|
| Planning trap | **HIGH** | Fatal | ✅ | 10:1 commit:plan ratio |
| Siyaada drops | HIGH | Severe | ✅ | Telemetry + partial redaction fallback |
| Burhan mobile timeout | MEDIUM | High | ✅ | Profile-aware timeouts |
| Dev crew no automation | HIGH | High | ✅ | Nightly CI validation gate |
| Context collapse | HIGH | High | ✅ | CLAUDE.md < 120 lines, scoped sessions |
| HN premature exposure | MEDIUM | Severe | ✅ | Private repo or honest README |
| Solo burnout | HIGH | Severe | ✅ | Contributors by week 10 |
| Governance before code | MEDIUM | High | ✅ | Write GOV docs after code exists |
| Dual-brain is one process | MEDIUM | High | ✅ | Separate containers, OS-level separation |
| Token costs at scale | MEDIUM | High | ✅ | Default cache, cost display in CLI |

---

## THE ONE FAILURE THAT CANNOT BE PREVENTED

**mithaq solves the wrong problem for the wrong customer at the wrong time.**

This is the existential risk no premortem item above addresses.

The CBE-regulated Cairo pilot assumes those banks want automated
security tooling. They may not. They may want a consultant relationship,
not a product. The $0 infrastructure pitch may signal "low quality" to
enterprise procurement. The Arabic-first positioning may resonate with
2 people in the org and create friction with the 8 people who evaluate
in English.

**How to test this before building:**
Before writing one more line of code, have 3 conversations with
actual security engineers at Egyptian banks. Not pitches — interviews.
Ask: what tool do you use today? What would have to be true for you
to switch? What would you pay?

If the answer is "we use Burp Suite and we're happy with it" — the
market insight is wrong and no amount of architecture makes mithaq viable.

If the answer is "we can't send our APKs to any cloud tool and we have
no good local alternative" — you have found your first customer.

---

## PRESCRIPTIONS (what to do NOW based on this premortem)

**Today:**
1. Adopt CLAUDE_COMPRESSED.md — under 120 lines, never grow it
2. One scoped Claude Code session per broken item — not all six at once
3. Wire Siyaada telemetry to stderr output before any other work

**This week:**
4. Write a partial redaction fallback for Siyaada (preserve structure, redact identifier)
5. Profile-aware timeout: WEB_POC_TIMEOUT=30, MOBILE_POC_TIMEOUT=120
6. Nightly GitHub Actions workflow: start DVWA + run validation gate + open PRs

**This month:**
7. Have 3 user interviews with Egyptian/MENA bank security engineers
8. Create 5 labeled "good first issues" for community contributors
9. Write CONTRIBUTING.md (not GOV-01 — that comes in Phase 5)
10. Set repo to private OR rewrite README to match 3-scanner reality

**The hard truth:**
The architecture is correct. The planning is excellent. The governance
documents are better than most enterprise tools have at v1.0.

None of that matters if the code doesn't work and nobody uses it.

The next 6 months must be dominated by commits, not documents.

