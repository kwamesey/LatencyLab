from __future__ import annotations
import os
from typing import List, Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import SQLModel, Field, create_engine, Session, select

DB_URL = os.getenv('DB_URL', 'sqlite:///./latency.db')
engine = create_engine(DB_URL, echo=False)

class Metric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp_ms: int
    target: str
    latency_ms: float | None
    jitter_ms: float
    packet_loss_pct: float

def init_db():
    SQLModel.metadata.create_all(engine)

app = FastAPI(title='latency-lab')

@app.on_event('startup')
def on_startup():
    init_db()

@app.post('/v1/metrics')
async def ingest_metrics(items: List[Metric]):
    with Session(engine) as sess:
        for it in items:
            sess.add(Metric(**it.dict()))
        sess.commit()
    return {'ok': True, 'count': len(items)}

DASHBOARD_HTML = '''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>latency-lab</title>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 2rem; }
      .card { padding: 1rem; border: 1px solid #ddd; border-radius: 12px; margin-bottom: 1rem; }
      h1 { margin-top: 0; }
      canvas { width: 100%; max-width: 900px; height: 360px; }
      .pill { display:inline-block;padding:.25rem .5rem;border-radius:999px;background:#f5f5f5;margin-right:.5rem; }
    </style>
  </head>
  <body>
    <h1>latency-lab</h1>
    <div class="card">
      <div hx-get="/v1/targets" hx-trigger="load, every 5s" hx-swap="innerHTML"></div>
    </div>
    <div class="card">
      <h3>Latency (ms)</h3>
      <canvas id="latencyChart"></canvas>
    </div>
    <script>
      async function fetchSeries() {
        const r = await fetch('/v1/series');
        return r.json();
      }
      const ctx = document.getElementById('latencyChart').getContext('2d');
      const chart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: {
          animation: false,
          scales: { x: { title: { display: true, text: 't' } }, y: { title: { display: true, text: 'ms' } } }
        }
      });
      async function refresh() {
        const data = await fetchSeries();
        chart.data.labels = data.labels;
        chart.data.datasets = data.datasets;
        chart.update();
      }
      setInterval(refresh, 3000);
      refresh();
    </script>
  </body>
</html>
'''

@app.get('/', response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(DASHBOARD_HTML)

@app.get('/v1/targets', response_class=HTMLResponse)
async def list_targets():
    with Session(engine) as sess:
        stmt = select(Metric.target).distinct()
        targets = [row[0] for row in sess.exec(stmt)]
    pills = ''.join(f'<span class="pill">{t}</span>' for t in targets) or '<em>No data yet</em>'
    return HTMLResponse(pills)

@app.get('/v1/series')
async def series():
    N = 50
    with Session(engine) as sess:
        stmt = select(Metric).order_by(Metric.timestamp_ms.desc()).limit(1000)
        rows = list(reversed(list(sess.exec(stmt))))
    by_target = {}
    for r in rows[-N:]:
        by_target.setdefault(r.target, []).append(r.latency_ms if r.latency_ms is not None else None)
    datasets = []
    for i, (t, vals) in enumerate(sorted(by_target.items())):
        datasets.append({
            'label': t,
            'data': vals,
            'fill': False,
            'tension': 0.2
        })
    return JSONResponse({'labels': list(range(len(next(iter(by_target.values()), [])))), 'datasets': datasets})
