from __future__ import annotations

import time
from collections import Counter, deque
from statistics import mean
from threading import Lock
from typing import Any

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []
METRIC_EVENTS: deque[dict[str, Any]] = deque(maxlen=1000)
_LOCK = Lock()


def record_request(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
) -> None:
    global TRAFFIC
    with _LOCK:
        TRAFFIC += 1
        REQUEST_LATENCIES.append(latency_ms)
        REQUEST_COSTS.append(cost_usd)
        REQUEST_TOKENS_IN.append(tokens_in)
        REQUEST_TOKENS_OUT.append(tokens_out)
        QUALITY_SCORES.append(quality_score)
        METRIC_EVENTS.append(
            {
                "timestamp": time.time(),
                "status": "success",
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "quality_score": quality_score,
            }
        )


def record_error(error_type: str) -> None:
    with _LOCK:
        ERRORS[error_type] += 1
        METRIC_EVENTS.append(
            {"timestamp": time.time(), "status": "error", "error_type": error_type}
        )


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def snapshot() -> dict[str, Any]:
    with _LOCK:
        now = time.time()
        events = list(METRIC_EVENTS)
        error_count = sum(ERRORS.values())
        request_count = TRAFFIC + error_count
        error_rate_pct = (error_count / request_count * 100) if request_count else 0.0
        hourly_cost = sum(
            event.get("cost_usd", 0.0)
            for event in events
            if event["timestamp"] >= now - 3600
        )
        daily_cost = sum(
            event.get("cost_usd", 0.0)
            for event in events
            if event["timestamp"] >= now - 86400
        )
        latency_p50 = percentile(REQUEST_LATENCIES, 50)
        latency_p95 = percentile(REQUEST_LATENCIES, 95)
        latency_p99 = percentile(REQUEST_LATENCIES, 99)

        return {
            "traffic": TRAFFIC,
            "request_count": request_count,
            "success_count": TRAFFIC,
            "error_count": error_count,
            "error_rate_pct": round(error_rate_pct, 4),
            "latency_p50": latency_p50,
            "latency_p95": latency_p95,
            "latency_p99": latency_p99,
            "latency_p50_ms": latency_p50,
            "latency_p95_ms": latency_p95,
            "latency_p99_ms": latency_p99,
            "avg_cost_usd": round(mean(REQUEST_COSTS), 6) if REQUEST_COSTS else 0.0,
            "total_cost_usd": round(sum(REQUEST_COSTS), 6),
            "hourly_cost_usd": round(hourly_cost, 6),
            "daily_cost_usd": round(daily_cost, 6),
            "tokens_in_total": sum(REQUEST_TOKENS_IN),
            "tokens_out_total": sum(REQUEST_TOKENS_OUT),
            "error_breakdown": dict(ERRORS),
            "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
            "series": events,
        }
