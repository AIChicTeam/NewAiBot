# utils/runpod_start.py
import os
import time
import runpod
from dotenv import load_dotenv

load_dotenv()

runpod.api_key = os.getenv("RUNPOD_API_KEY")
pod_id = "zhha0iny0yjd1c"

def is_pod_running(pod_id):
    pod_info = runpod.get_pod(pod_id)
    desired_status = pod_info.get("desiredStatus", "").upper()
    current_status = pod_info.get("status", "").lower()
    return desired_status == "RUNNING" or current_status == "running"

def start_pod_if_needed(pod_id, gpu_count=1):
    if not is_pod_running(pod_id):
        try:
            runpod.resume_pod(pod_id, gpu_count=gpu_count)
        except Exception as e:
            print(f"❌ Error starting pod: {e}")
            exit()

def wait_for_pod_info(pod_id, max_retries=30, delay=5):
    for _ in range(max_retries):
        pod_info = runpod.get_pod(pod_id)
        if pod_info.get("runtime", {}).get("ports"):
            return pod_info
        time.sleep(delay)
    return None

def ensure_pod_ready():
    start_pod_if_needed(pod_id, gpu_count=1)
    pod_info = wait_for_pod_info(pod_id)
    if not pod_info:
        raise RuntimeError("❌ Failed to retrieve pod info")
