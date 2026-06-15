from pathlib import Path

import yaml


def test_alert_rules_have_owners_and_runbooks() -> None:
    config = yaml.safe_load(Path("config/alert_rules.yaml").read_text(encoding="utf-8"))
    alerts = config["alerts"]

    assert len(alerts) >= 3
    for alert in alerts:
        assert alert["condition"]
        assert alert["owner"]
        runbook_path = Path(alert["runbook"].split("#", 1)[0])
        assert runbook_path.exists()


def test_slo_config_covers_dashboard_thresholds() -> None:
    config = yaml.safe_load(Path("config/slo.yaml").read_text(encoding="utf-8"))
    assert {
        "latency_p95_ms",
        "error_rate_pct",
        "daily_cost_usd",
        "quality_score_avg",
    }.issubset(config["slis"])
