# LocalCompute Commons - Quickstart Guide 🚀

This guide walks you through setting up and running **LocalCompute Commons** in under 5 minutes on your local development machine.

---

## 1. Prerequisites

- **Python 3.11+** installed
- **Node.js 18+ / 20+** and **npm** installed
- *(Optional)* Docker and Docker Compose (for complete containerized multi-node cluster)
- *(Optional)* [Ollama](https://ollama.com/) running locally on port 11434 with `llama3:8b` (built-in mock engine is active by default for instant offline runs).

---

## 2. Fast Local Development Setup

### Step 1: Install Python Core Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install and Build Frontend Web Dashboard
```bash
cd apps/web
npm install
npm run build
cd ../..
```

### Step 3: Start Coordinator Server
```bash
uvicorn apps.coordinator.main:app --host 0.0.0.0 --port 8000 --reload
```
The Coordinator API is now running at: `http://localhost:8000`  
Swagger API Documentation: `http://localhost:8000/docs`

### Step 4: Start Worker Node Daemon
In a new terminal window:
```bash
python examples/run_local_worker.py
```
This registers a worker node, reports hardware capabilities, and starts the heartbeat loop.

### Step 5: Start React Web Interface
In another terminal window:
```bash
cd apps/web
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 3. Pre-Configured Credentials

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `AdminLocalCompute2026!` | Full cluster access, approvals, revoking |
| **Operator** | `operator1` | `OperatorPassword2026!` | Node pause/resume, alerts, workloads |
| **Researcher** | `researcher1` | `ResearcherPassword2026!` | Workload submission, job queue inspection |

---

## 4. Submitting Your First Distributed Workload

### Via Web UI
1. Navigate to `http://localhost:5173`
2. Click **Submit Workload** in the navbar.
3. Select your desired privacy level (`trusted_nodes` or `local_only`).
4. Enter document chunks and click **Dispatch Workload to Grid**.
5. Switch to **Job Queue** to observe parallel task scheduling and real-time inference completion.

### Via Python Script
```bash
python examples/submit_batch_workload.py
```

---

## 5. Running the 40-Scenario Evaluation Suite
```bash
python tests/evaluation/run_evaluations.py
```
All 40 scenarios will run with full scoring, latency, and fault recovery measurements.
