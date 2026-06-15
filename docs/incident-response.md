# Incident Response Notes

## Investigation flow

1. Start with `/dashboard` to identify the breached signal and time window.
2. Open Langfuse traces from that window and compare the `rag-retrieval` and
   `llm-generation` observations.
3. Use the trace metadata `correlation_id` to find the matching JSON log lines.
4. Confirm the failure mode, disable the incident, and repeat the same request.

## Scenario: rag_slow

- Symptom: P95/P99 latency rises while error rate and token cost stay stable.
- Proof: the `rag-retrieval` span is approximately 2.5 seconds longer; the LLM
  generation duration remains near baseline.
- Root cause: the `rag_slow` toggle adds a delay in the retrieval layer.
- Mitigation: `python scripts/inject_incident.py --scenario rag_slow --disable`.
- Prevention: alert on sustained P95 latency and add a retrieval timeout with a
  fallback source.

## Scenario: tool_fail

- Symptom: error rate rises and responses return HTTP 500.
- Proof: logs contain `error_type=RuntimeError` for the affected correlation ID,
  and the trace fails in `rag-retrieval` before generation starts.
- Root cause: the retrieval tool raises `Vector store timeout`.
- Mitigation: disable the toggle and route to a fallback retrieval source.
- Prevention: use bounded retries, a circuit breaker, and an explicit tool SLO.

## Scenario: cost_spike

- Symptom: token output and hourly cost rise while latency and errors remain
  close to baseline.
- Proof: `llm-generation` usage shows roughly four times the output tokens.
- Root cause: the `cost_spike` toggle multiplies generated output tokens.
- Mitigation: disable the toggle and cap response tokens.
- Prevention: alert on cost versus baseline and route simple requests to a
  cheaper model.

Record the actual trace ID and matching log line in `docs/blueprint-template.md`
during the live exercise.
