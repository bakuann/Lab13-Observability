# Evidence Collection Sheet

## Required screenshots
- Langfuse trace list with >= 10 traces
- One full trace waterfall
- JSON logs showing correlation_id
- Log line with PII redaction
- Dashboard with 6 panels
- Alert rules with runbook link

The local dashboard is available at `http://127.0.0.1:8000/dashboard` after
starting the app. Capture it after running `python scripts/load_test.py` so all
six panels contain representative data.

## Optional screenshots
- Incident before/after fix
- Cost comparison before/after optimization
- Auto-instrumentation proof
