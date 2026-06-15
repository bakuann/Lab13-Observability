# Dashboard Spec

The `/metrics` endpoint exposes a current snapshot plus the latest 1,000 metric
events in `series`. Use a default time range of 1 hour and refresh every 15-30
seconds.

| Panel | Metric fields | Unit | Visualization | Threshold / SLO line |
|---|---|---|---|---|
| Latency percentiles | `latency_p50_ms`, `latency_p95_ms`, `latency_p99_ms` | ms | time series | P95 = 3,000 ms |
| Traffic | `request_count`, `success_count` | requests | stat + time series | none |
| Error rate | `error_rate_pct`, `error_breakdown` | percent / errors | stat + breakdown table | 2% |
| Cost | `hourly_cost_usd`, `daily_cost_usd`, `total_cost_usd` | USD | time series + stat | $2.50/day |
| Tokens | `tokens_in_total`, `tokens_out_total` | tokens | two-series chart | none |
| Quality proxy | `quality_avg` | score from 0 to 1 | gauge | 0.75 |

Keep these six panels on the main layer. The latency, error-rate, daily-cost,
and quality thresholds are sourced from `config/slo.yaml`.
