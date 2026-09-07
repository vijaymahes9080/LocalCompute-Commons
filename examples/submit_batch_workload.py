"""
Example Client: Submit a Privacy-Preserving Batch Summarization Workload
"""
import httpx
import json
import time

COORDINATOR_URL = "http://localhost:8000"

def main():
    print("1. Authenticating with Coordinator...")
    with httpx.Client() as client:
        auth_resp = client.post(
            f"{COORDINATOR_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "AdminLocalCompute2026!"}
        )
        if auth_resp.status_code != 200:
            print(f"Auth failed: {auth_resp.text}")
            return
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ Authenticated as Administrator.")

        # Read sample text chunks
        payload = {
            "title": "College AI Lab: Distributed Inference Benchmark",
            "workload_type": "summarization",
            "privacy_class": "trusted_nodes",
            "required_model": "llama3:8b",
            "priority": 8,
            "documents": [
                {
                    "text": "Abstract: Distributed compute-sharing enables resource-constrained universities to train and serve open-weight foundation models locally."
                },
                {
                    "text": "Methodology: We partition large document corpora into independent semantic sections and score candidate worker nodes based on CPU, VRAM, and power metrics."
                },
                {
                    "text": "Results: The deterministic scheduler completed 50 tasks across 3 worker nodes with zero lease timeouts and 100% cryptographic audit verification."
                }
            ]
        }

        print("\n2. Submitting batch workload...")
        sub_resp = client.post(
            f"{COORDINATOR_URL}/api/v1/workloads/submit",
            json=payload,
            headers=headers
        )
        if sub_resp.status_code != 200:
            print(f"Submission failed: {sub_resp.text}")
            return

        job = sub_resp.json()
        job_id = job["id"]
        print(f"✓ Workload created successfully! Job ID: {job_id}")
        print(f"  Total Tasks: {job['total_tasks']}, State: {job['state']}")

        # Poll until complete
        print("\n3. Polling Job Execution Progress...")
        for _ in range(15):
            time.sleep(2)
            poll_resp = client.get(f"{COORDINATOR_URL}/api/v1/jobs/{job_id}", headers=headers)
            job_data = poll_resp.json()
            print(f"  Progress: {job_data['succeeded_tasks']}/{job_data['total_tasks']} completed | State: {job_data['state']}")
            if job_data["state"] in ["succeeded", "failed"]:
                break

        print("\n4. Final Result Summary:")
        print(job_data.get("aggregated_result") or "No result generated.")

if __name__ == "__main__":
    main()
