# latency-lab 🚀

A **network telemetry & visualization** project designed to look great on your GitHub and impress SWE recruiters.

**What it is:**  
- A tiny observability stack that measures **latency, jitter, and packet loss** to any set of targets.  
- A lightweight **Agent** (CLI) that collects metrics and posts them to the **Server** (FastAPI).  
- A clean, zero-JS-build **Dashboard** (HTMX + Chart.js CDN) to visualize metrics in real time.

**Why it's impressive:**  
- Systems-y: async I/O, structured logs, graceful shutdown, retry/backoff, pydantic schemas.  
- Networking: ICMP/`ping` integration, jitter calculation, rolling windows.  
- Backend: FastAPI, dependency-injected services, typed models, tests & CI.  
- DevEx: `docker-compose up` to run; `pytest` + linting in CI; MIT license.

---

## Architecture

