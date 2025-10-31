# latency-lab 🚀  
**Network Telemetry + Real-Time Visualization**

This is a project I built to combine my interests in **networking, backend systems, and real-time data visualization**.  
`latency-lab` is a lightweight observability stack that measures latency, jitter, and packet loss across multiple targets, then visualizes everything in a clean dashboard.  

---

## 💡 Why I Built It
I wanted to create something that felt like a real-world engineering tool — something that touches async systems, REST APIs, and live dashboards all in one stack.  
`latency-lab` is meant to show what I can do across multiple areas:
- **Systems thinking:** async I/O, retry logic, structured logging  
- **Networking:** ICMP ping probing, jitter + packet-loss tracking  
- **Backend:** FastAPI server, SQLite database, JSON APIs  
- **Frontend:** real-time visualization using HTMX + Chart.js  
- **DevOps:** containerized setup with Docker + GitHub Actions CI  

---

## ⚙️ Architecture
Agent (CLI)
│
├── sends JSON metrics via HTTP POST → FastAPI Server (/v1/metrics)
│
├── Server stores results → SQLite database
│
└── Dashboard (HTMX + Chart.js) pulls data → renders live latency graphs

**Data Flow Summary:**  
1. The **Agent** pings specified targets (e.g., 1.1.1.1, 8.8.8.8) asynchronously.  
2. Results (latency, jitter, packet loss) are sent to the **FastAPI Server**.  
3. The **Server** stores the metrics in an SQLite database.  
4. The **Dashboard** uses HTMX to poll updates and display live charts via Chart.js.  

---

## 🚀 Quickstart

```bash
# 1. Create and activate a venv (recommended)
python3 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python -m latency_lab.server

# 4. Run the agent (in another shell)
python -m latency_lab.agent --targets 1.1.1.1,8.8.8.8 --interval 5

# 5. Open the dashboard
open http://127.0.0.1:8000
