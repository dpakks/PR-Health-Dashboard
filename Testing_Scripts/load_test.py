"""
Load Test Script for PR Health Dashboard
-----------------------------------------
Sends concurrent requests to the ALB to:
1. Verify ALB is distributing traffic
2. Trigger ECS auto scaling (CPU > 70%)

Run: python load_test.py
"""

import threading
import time
import urllib.request
import urllib.error
import json
import ssl

# =====================================================
# Configuration
# =====================================================
API_URL = "https://api.prmonitor.site"
CONCURRENT_USERS = 500       # Number of simultaneous threads
REQUESTS_PER_USER = 500     # Each thread sends this many requests
DELAY_BETWEEN = 0.01        # Seconds between requests per thread

# =====================================================
# Counters (thread-safe)
# =====================================================
lock = threading.Lock()
stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "status_codes": {},
}

# Ignore SSL verification for simplicity
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def make_request(url):
    """Make a single GET request and track the result."""
    try:
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, context=ssl_context, timeout=10)
        code = response.getcode()

        with lock:
            stats["total"] += 1
            stats["success"] += 1
            stats["status_codes"][code] = stats["status_codes"].get(code, 0) + 1

    except urllib.error.HTTPError as e:
        with lock:
            stats["total"] += 1
            stats["failed"] += 1
            stats["status_codes"][e.code] = stats["status_codes"].get(e.code, 0) + 1

    except Exception as e:
        with lock:
            stats["total"] += 1
            stats["failed"] += 1
            stats["status_codes"]["error"] = stats["status_codes"].get("error", 0) + 1


def user_session(user_id):
    """Simulate a single user sending multiple requests."""
    endpoints = [
        "/",
        "/docs",
        "/openapi.json",
    ]

    for i in range(REQUESTS_PER_USER):
        endpoint = endpoints[i % len(endpoints)]
        url = f"{API_URL}{endpoint}"
        make_request(url)
        time.sleep(DELAY_BETWEEN)


def print_live_stats(stop_event):
    """Print stats every 5 seconds while test is running."""
    while not stop_event.is_set():
        time.sleep(5)
        with lock:
            elapsed = time.time() - start_time
            rps = stats["total"] / elapsed if elapsed > 0 else 0
            print(
                f"  [{elapsed:.0f}s] "
                f"Total: {stats['total']} | "
                f"Success: {stats['success']} | "
                f"Failed: {stats['failed']} | "
                f"RPS: {rps:.1f}"
            )


if __name__ == "__main__":
    print("=" * 60)
    print("  LOAD TEST — PR Health Dashboard")
    print("=" * 60)
    print(f"  Target:     {API_URL}")
    print(f"  Users:      {CONCURRENT_USERS}")
    print(f"  Requests:   {CONCURRENT_USERS * REQUESTS_PER_USER} total")
    print("=" * 60)
    print()

    # Quick health check first
    print("Checking API health...")
    try:
        req = urllib.request.Request(f"{API_URL}/")
        resp = urllib.request.urlopen(req, context=ssl_context, timeout=5)
        data = json.loads(resp.read().decode())
        print(f"  API is up: {data}")
    except Exception as e:
        print(f"  API is down: {e}")
        print("  Aborting load test.")
        exit(1)

    print()
    print("Starting load test...")
    print()

    start_time = time.time()

    # Start live stats printer
    stop_event = threading.Event()
    stats_thread = threading.Thread(
        target=print_live_stats, args=(stop_event,), daemon=True
    )
    stats_thread.start()

    # Launch all user threads
    threads = []
    for i in range(CONCURRENT_USERS):
        t = threading.Thread(target=user_session, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.02)  # Stagger thread starts slightly

    # Wait for all threads to finish
    for t in threads:
        t.join()

    stop_event.set()
    end_time = time.time()
    duration = end_time - start_time

    # Final report
    print()
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Duration:       {duration:.1f} seconds")
    print(f"  Total requests: {stats['total']}")
    print(f"  Successful:     {stats['success']}")
    print(f"  Failed:         {stats['failed']}")
    print(f"  Avg RPS:        {stats['total'] / duration:.1f}")
    print(f"  Status codes:   {stats['status_codes']}")
    print("=" * 60)
    print()
    print("Now check ECS auto scaling:")
    print("  aws ecs describe-services --cluster pr-dashboard-cluster --services pr-dashboard-backend-service --query \"services[0].{running:runningCount,desired:desiredCount}\"")
    print()
    print("And check CloudWatch metrics in the AWS console:")
    print("  ECS > Clusters > pr-dashboard-cluster > Metrics tab")