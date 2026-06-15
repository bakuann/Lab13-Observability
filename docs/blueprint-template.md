# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: bakuann-solo
- [REPO_URL]: https://github.com/bakuann/Lab13-Observability
- [MEMBERS]:
  - Member A: Phùng Bá Quân | Role: Solo developer - Logging, PII, Tracing, SLO, Alerts, Dashboard, Demo, and Report
  - Member B: N/A | Role: Covered by Member A
  - Member C: N/A | Role: Covered by Member A
  - Member D: N/A | Role: Covered by Member A
  - Member E: N/A | Role: Covered by Member A

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 14 requests generated with tracing enabled; confirm the accepted count is at least 10 in the Langfuse UI
- [PII_LEAKS_FOUND]: 0

Verification summary from `python scripts/validate_logs.py`:
- 43 JSON log records analyzed
- 0 records missing required fields
- 0 API records missing enrichment fields
- 15 unique correlation IDs
- 0 potential PII leaks

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: Pending capture at `docs/evidence/correlation-id-log.png`; use correlation ID `req-58279129` from `data/logs.jsonl`
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: Pending capture at `docs/evidence/pii-redaction-log.png`; the sample email is logged as `[REDACTED_EMAIL]`
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Pending capture at `docs/evidence/langfuse-trace-waterfall.png`
- [TRACE_WATERFALL_EXPLANATION]: The root `agent-run` observation contains two important child observations. `rag-retrieval` shows retrieval duration, document count, and whether `rag_slow` was active. `llm-generation` shows the model plus input/output token usage. Comparing these observations distinguishes retrieval latency from model latency or token-cost growth. Trace metadata includes the hashed user ID, session ID, feature, model, environment, quality score, and correlation ID without sending raw PII.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: Pending capture at `docs/evidence/dashboard-six-panels.png`; open `http://127.0.0.1:8000/dashboard` after running the load test
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 157ms in the local sample |
| Error Rate | < 2% | 28d | 0.00% in the local sample |
| Cost Budget | < $2.5/day | 1d | $0.030120 total sample cost |
| Quality Average | >= 0.75 | 28d | Available live from `/metrics` as `quality_avg` |

The dashboard provides exactly six panels: latency P50/P95/P99, traffic,
error rate and breakdown, cost, tokens in/out, and quality proxy. It uses a
one-hour window, refreshes every 20 seconds, displays units, and includes SLO
thresholds.

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: Pending capture at `docs/evidence/alert-rules.png`; source is `config/alert_rules.yaml`
- [SAMPLE_RUNBOOK_LINK]: [High latency P95 runbook](alerts.md#1-high-latency-p95)

Configured alerts:
- P2 high latency: `latency_p95_ms > 5000 for 30m`
- P1 high error rate: `error_rate_pct > 5 for 5m`
- P2 cost spike: `hourly_cost_usd > 2x_baseline for 15m`

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 and P99 latency increase while error rate, token usage, and LLM generation latency remain near baseline.
- [ROOT_CAUSE_PROVED_BY]: The Langfuse `rag-retrieval` observation should increase by approximately 2.5 seconds and contain `rag_slow=true`. Use its trace metadata `correlation_id` to locate the matching `request_received` and `response_sent` JSON log lines. Record the actual trace ID here after the live run: `PENDING_TRACE_ID`.
- [FIX_ACTION]: Disable the injected incident with `python scripts/inject_incident.py --scenario rag_slow --disable`, then rerun the same request and compare the new trace and latency.
- [PREVENTIVE_MEASURE]: Add a retrieval timeout, fallback retrieval source, and sustained P95 alert. Keep the metrics-to-traces-to-logs investigation procedure documented in `docs/incident-response.md`.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]: bakuann
- [TASKS_COMPLETED]: Completed the lab solo: implemented correlation-ID propagation and response headers; structured and enriched JSON logging; recursive PII redaction and user-ID hashing; Langfuse SDK v3 tracing with RAG and LLM observations; thread-safe traffic, latency, error, cost, token, and quality metrics; six-panel dashboard; SLO and alert configuration; incident runbook; deterministic answer-quality behavior; and unit/integration/configuration tests. Final verification reached 100/100 with 0 PII leaks and all tests passing.
- [EVIDENCE_LINK]: [Commit 612df0d](https://github.com/bakuann/Lab13-Observability/commit/612df0d)

### [MEMBER_B_NAME]: N/A - solo submission
- [TASKS_COMPLETED]: Covered by bakuann under Member A.
- [EVIDENCE_LINK]: [Commit 612df0d](https://github.com/bakuann/Lab13-Observability/commit/612df0d)

### [MEMBER_C_NAME]: N/A - solo submission
- [TASKS_COMPLETED]: Covered by bakuann under Member A.
- [EVIDENCE_LINK]: [Commit 612df0d](https://github.com/bakuann/Lab13-Observability/commit/612df0d)

### [MEMBER_D_NAME]: N/A - solo submission
- [TASKS_COMPLETED]: Covered by bakuann under Member A.
- [EVIDENCE_LINK]: [Commit 612df0d](https://github.com/bakuann/Lab13-Observability/commit/612df0d)

### [MEMBER_E_NAME]: N/A - solo submission
- [TASKS_COMPLETED]: Covered by bakuann under Member A.
- [EVIDENCE_LINK]: [Commit 612df0d](https://github.com/bakuann/Lab13-Observability/commit/612df0d)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: The metrics endpoint exposes average, total, hourly, and daily cost. The cost runbook recommends shorter prompts, cheaper-model routing for simple requests, response-token caps, and prompt caching. Evidence: `app/metrics.py`, `docs/alerts.md`, and the dashboard Cost panel.
- [BONUS_AUDIT_LOGS]: Not claimed. `AUDIT_LOG_PATH` is reserved in `.env.example`, but a separate audit pipeline is not implemented.
- [BONUS_CUSTOM_METRIC]: Implemented a heuristic quality score from 0 to 1, exported as `quality_avg`, shown on the dashboard with a 0.75 target, and covered by expected-answer tests.

## Final Submission Checklist

- [x] `python scripts/validate_logs.py` returns 100/100
- [x] Correlation IDs propagate through response and logs
- [x] PII validation reports zero leaks
- [x] Dashboard contains six panels
- [x] Three alerts include owners and runbook links
- [x] Solo contribution is linked to commit `612df0d`
- [ ] Confirm at least 10 accepted traces in Langfuse
- [ ] Run `rag_slow` live and replace `PENDING_TRACE_ID`
- [ ] Capture the five screenshots listed under `docs/evidence/`
