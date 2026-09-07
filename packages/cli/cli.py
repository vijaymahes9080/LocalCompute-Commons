"""
LocalCompute Commons - Interactive Terminal CLI Tool
"""
import sys
import os
import argparse
import httpx
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from packages.shared.config import settings

COORDINATOR_URL = f"http://{settings.COORDINATOR_HOST}:{settings.COORDINATOR_PORT}"

def login_client() -> httpx.Client:
    client = httpx.Client(base_url=COORDINATOR_URL, timeout=10.0)
    try:
        resp = client.post("/api/v1/auth/login", json={
            "username": settings.DEFAULT_ADMIN_USERNAME,
            "password": settings.DEFAULT_ADMIN_PASSWORD
        })
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            client.headers.update({"Authorization": f"Bearer {token}"})
    except Exception as exc:
        print(f"Warning: Could not connect to coordinator at {COORDINATOR_URL}: {exc}")
    return client

def cmd_nodes(args):
    client = login_client()
    try:
        resp = client.get("/api/v1/nodes")
        nodes = resp.json()
        print(f"\n{'NODE ID':<20} {'NODE NAME':<25} {'STATUS':<10} {'TRUST':<15} {'CORES':<8} {'RAM (GB)':<10}")
        print("-" * 90)
        for n in nodes:
            cap = n.get("capabilities", {})
            ram_gb = round(cap.get("memory_available_mb", 0) / 1024, 1)
            print(f"{n['node_id']:<20} {n['node_name']:<25} {n['status']:<10} {n['trust_level']:<15} {cap.get('cpu_cores', '-'):<8} {ram_gb:<10}")
        print(f"\nTotal Nodes: {len(nodes)}\n")
    except Exception as exc:
        print(f"Error fetching nodes: {exc}")

def cmd_status(args):
    client = login_client()
    try:
        resp = client.get("/api/v1/capacity/snapshot")
        data = resp.json()
        print("\n=== CLUSTER COMPUTE SNAPSHOT ===")
        print(f"Online Nodes:     {data.get('online_nodes')} / {data.get('total_nodes')}")
        print(f"Total CPU Cores:  {data.get('available_cpu_cores')} Available / {data.get('total_cpu_cores')} Total")
        print(f"Memory (RAM):     {data.get('available_memory_gb')} GB Available / {data.get('total_memory_gb')} GB Total")
        print(f"VRAM (GPU):       {data.get('available_vram_gb')} GB Available / {data.get('total_vram_gb')} GB Total")
        print(f"Active Jobs:      {data.get('active_jobs')}")
        print(f"Pending Tasks:    {data.get('pending_tasks')}")
        print(f"Avg Queue Wait:   {data.get('avg_queue_wait_seconds')}s\n")
    except Exception as exc:
        print(f"Error fetching status: {exc}")

def cmd_submit(args):
    client = login_client()
    payload = {
        "title": args.title or "CLI Batch Summarization",
        "workload_type": "summarization",
        "privacy_class": args.privacy or "trusted_nodes",
        "required_model": args.model or "llama3:8b",
        "priority": args.priority or 5,
        "documents": [{"text": t} for t in args.text]
    }
    try:
        resp = client.post("/api/v1/workloads/submit", json=payload)
        job = resp.json()
        print(f"\n✓ Workload submitted successfully! Job ID: {job.get('id')}")
        print(f"  Total Tasks: {job.get('total_tasks')}, Initial State: {job.get('state')}\n")
    except Exception as exc:
        print(f"Error submitting workload: {exc}")

def main():
    parser = argparse.ArgumentParser(prog="lc", description="LocalCompute Commons Terminal CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Nodes
    subparsers.add_parser("nodes", help="List active worker compute nodes")
    
    # Status
    subparsers.add_parser("status", help="Display cluster capacity and active queue status")
    
    # Submit
    submit_p = subparsers.add_parser("submit", help="Submit batch AI workload")
    submit_p.add_argument("--title", type=str, default="CLI Workload")
    submit_p.add_argument("--model", type=str, default="llama3:8b")
    submit_p.add_argument("--privacy", type=str, default="trusted_nodes")
    submit_p.add_argument("--priority", type=int, default=5)
    submit_p.add_argument("--text", nargs="+", required=True, help="Text chunks to summarize")

    args = parser.parse_args()
    if args.command == "nodes":
        cmd_nodes(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "submit":
        cmd_submit(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
