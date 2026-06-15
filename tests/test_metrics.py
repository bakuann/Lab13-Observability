from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_exposes_dashboard_and_alert_metrics(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    metrics.REQUEST_LATENCIES.clear()
    metrics.REQUEST_COSTS.clear()
    metrics.REQUEST_TOKENS_IN.clear()
    metrics.REQUEST_TOKENS_OUT.clear()
    metrics.QUALITY_SCORES.clear()
    metrics.ERRORS.clear()
    metrics.METRIC_EVENTS.clear()

    metrics.record_request(250, 0.25, 100, 50, 0.9)
    metrics.record_error("RuntimeError")
    result = metrics.snapshot()

    assert result["request_count"] == 2
    assert result["error_rate_pct"] == 50.0
    assert result["latency_p95_ms"] == 250.0
    assert result["hourly_cost_usd"] == 0.25
    assert result["daily_cost_usd"] == 0.25
    assert result["error_breakdown"] == {"RuntimeError": 1}
