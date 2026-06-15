from __future__ import annotations

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 13 Observability Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #08111f;
      --panel: #101d2f;
      --line: #243650;
      --text: #e7eef8;
      --muted: #8fa4bf;
      --accent: #55d6be;
      --warning: #f6c85f;
      --danger: #ff6b6b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top left, #142844 0, var(--bg) 42%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 36px 0 52px; }
    header { display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 24px; }
    h1 { margin: 0 0 6px; font-size: clamp(1.7rem, 4vw, 2.6rem); letter-spacing: -0.04em; }
    header p, .meta, .unit { color: var(--muted); }
    header p { margin: 0; }
    .status { text-align: right; font-size: 0.86rem; }
    .status strong { display: block; color: var(--accent); margin-bottom: 4px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .panel {
      min-height: 248px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: linear-gradient(145deg, rgba(20, 37, 59, 0.98), rgba(12, 25, 42, 0.98));
      box-shadow: 0 20px 45px rgba(0, 0, 0, 0.18);
    }
    .panel-head { display: flex; justify-content: space-between; gap: 16px; align-items: start; }
    h2 { margin: 0; font-size: 1rem; letter-spacing: 0.01em; }
    .threshold { color: var(--muted); font-size: 0.75rem; border: 1px solid var(--line); padding: 4px 8px; border-radius: 999px; }
    .metric { margin: 18px 0 2px; font-size: 2.1rem; font-weight: 750; letter-spacing: -0.04em; }
    .metric.warning { color: var(--warning); }
    .metric.danger { color: var(--danger); }
    .details { display: flex; flex-wrap: wrap; gap: 8px 16px; min-height: 22px; color: var(--muted); font-size: 0.82rem; }
    canvas { width: 100%; height: 82px; margin-top: 18px; display: block; }
    .bar { height: 7px; margin-top: 16px; overflow: hidden; border-radius: 999px; background: #1b2c43; }
    .bar span { display: block; height: 100%; width: 0; background: var(--accent); transition: width 220ms ease; }
    .error { color: var(--danger); }
    @media (max-width: 760px) {
      header { align-items: start; flex-direction: column; }
      .status { text-align: left; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Service health, at a glance</h1>
        <p>Six operational signals from the Day 13 agent. Window: last 1 hour.</p>
      </div>
      <div class="status">
        <strong id="refresh-state">Loading metrics...</strong>
        <span>Auto refresh every 20 seconds</span>
      </div>
    </header>

    <div class="grid">
      <section class="panel" data-testid="latency-panel">
        <div class="panel-head"><h2>Latency percentiles</h2><span class="threshold">P95 SLO 3,000 ms</span></div>
        <div class="metric" id="latency-p95">--</div>
        <div class="details"><span id="latency-p50">P50 --</span><span id="latency-p99">P99 --</span></div>
        <canvas id="latency-chart" aria-label="Latency history"></canvas>
      </section>

      <section class="panel" data-testid="traffic-panel">
        <div class="panel-head"><h2>Traffic</h2><span class="threshold">Requests</span></div>
        <div class="metric" id="request-count">--</div>
        <div class="details"><span id="success-count">-- successful</span><span id="traffic-errors">-- failed</span></div>
        <canvas id="traffic-chart" aria-label="Traffic history"></canvas>
      </section>

      <section class="panel" data-testid="errors-panel">
        <div class="panel-head"><h2>Error rate</h2><span class="threshold">SLO below 2%</span></div>
        <div class="metric" id="error-rate">--</div>
        <div class="details"><span id="error-breakdown">No errors recorded</span></div>
        <canvas id="error-chart" aria-label="Error history"></canvas>
      </section>

      <section class="panel" data-testid="cost-panel">
        <div class="panel-head"><h2>Cost</h2><span class="threshold">Budget $2.50/day</span></div>
        <div class="metric" id="daily-cost">--</div>
        <div class="details"><span id="hourly-cost">1h --</span><span id="total-cost">Total --</span></div>
        <canvas id="cost-chart" aria-label="Cost history"></canvas>
      </section>

      <section class="panel" data-testid="tokens-panel">
        <div class="panel-head"><h2>Token usage</h2><span class="threshold">Tokens</span></div>
        <div class="metric" id="tokens-total">--</div>
        <div class="details"><span id="tokens-in">In --</span><span id="tokens-out">Out --</span></div>
        <canvas id="tokens-chart" aria-label="Token history"></canvas>
      </section>

      <section class="panel" data-testid="quality-panel">
        <div class="panel-head"><h2>Quality proxy</h2><span class="threshold">Target 0.75</span></div>
        <div class="metric" id="quality-score">--</div>
        <div class="details"><span>Heuristic score from 0 to 1</span></div>
        <div class="bar"><span id="quality-bar"></span></div>
        <canvas id="quality-chart" aria-label="Quality history"></canvas>
      </section>
    </div>
  </main>

  <script>
    const oneHourAgo = () => Date.now() / 1000 - 3600;
    const number = (value, digits = 0) => Number(value || 0).toLocaleString(undefined, {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    });
    const money = (value) => `$${number(value, 4)}`;

    function setMetric(id, text, state = "") {
      const element = document.getElementById(id);
      element.textContent = text;
      element.className = `metric ${state}`.trim();
    }

    function drawChart(id, values, color = "#55d6be") {
      const canvas = document.getElementById(id);
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.max(320, canvas.clientWidth * ratio);
      canvas.height = 82 * ratio;
      const context = canvas.getContext("2d");
      context.scale(ratio, ratio);
      const width = canvas.width / ratio;
      const height = canvas.height / ratio;
      context.clearRect(0, 0, width, height);
      context.strokeStyle = "#243650";
      context.beginPath();
      context.moveTo(0, height - 1);
      context.lineTo(width, height - 1);
      context.stroke();
      if (!values.length) return;
      const maximum = Math.max(...values, 1);
      context.strokeStyle = color;
      context.lineWidth = 2;
      context.beginPath();
      values.forEach((value, index) => {
        const x = values.length === 1 ? width : index * width / (values.length - 1);
        const y = height - 5 - (value / maximum) * (height - 12);
        index === 0 ? context.moveTo(x, y) : context.lineTo(x, y);
      });
      context.stroke();
    }

    async function refresh() {
      const state = document.getElementById("refresh-state");
      try {
        const response = await fetch("/metrics", { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const events = (data.series || []).filter((event) => event.timestamp >= oneHourAgo());
        const p95State = data.latency_p95_ms > 3000 ? "danger" : "";
        const errorState = data.error_rate_pct > 2 ? "danger" : "";
        const costState = data.daily_cost_usd > 2.5 ? "warning" : "";
        const qualityState = data.quality_avg < 0.75 ? "warning" : "";

        setMetric("latency-p95", `${number(data.latency_p95_ms)} ms P95`, p95State);
        document.getElementById("latency-p50").textContent = `P50 ${number(data.latency_p50_ms)} ms`;
        document.getElementById("latency-p99").textContent = `P99 ${number(data.latency_p99_ms)} ms`;
        setMetric("request-count", number(data.request_count));
        document.getElementById("success-count").textContent = `${number(data.success_count)} successful`;
        document.getElementById("traffic-errors").textContent = `${number(data.error_count)} failed`;
        setMetric("error-rate", `${number(data.error_rate_pct, 2)}%`, errorState);
        const breakdown = Object.entries(data.error_breakdown || {}).map(([key, value]) => `${key}: ${value}`);
        document.getElementById("error-breakdown").textContent = breakdown.join(" | ") || "No errors recorded";
        setMetric("daily-cost", money(data.daily_cost_usd), costState);
        document.getElementById("hourly-cost").textContent = `1h ${money(data.hourly_cost_usd)}`;
        document.getElementById("total-cost").textContent = `Total ${money(data.total_cost_usd)}`;
        setMetric("tokens-total", number(data.tokens_in_total + data.tokens_out_total));
        document.getElementById("tokens-in").textContent = `In ${number(data.tokens_in_total)}`;
        document.getElementById("tokens-out").textContent = `Out ${number(data.tokens_out_total)}`;
        setMetric("quality-score", number(data.quality_avg, 2), qualityState);
        document.getElementById("quality-bar").style.width = `${Math.min(100, data.quality_avg * 100)}%`;

        drawChart("latency-chart", events.map((event) => event.latency_ms || 0));
        drawChart("traffic-chart", events.map((_, index) => index + 1));
        drawChart("error-chart", events.map((event) => event.status === "error" ? 1 : 0), "#ff6b6b");
        drawChart("cost-chart", events.map((event) => event.cost_usd || 0), "#f6c85f");
        drawChart("tokens-chart", events.map((event) => (event.tokens_in || 0) + (event.tokens_out || 0)));
        drawChart("quality-chart", events.map((event) => event.quality_score || 0));

        state.textContent = `Healthy feed - updated ${new Date().toLocaleTimeString()}`;
        state.className = "";
      } catch (error) {
        state.textContent = `Metrics unavailable: ${error.message}`;
        state.className = "error";
      }
    }

    refresh();
    window.setInterval(refresh, 20000);
  </script>
</body>
</html>
"""
