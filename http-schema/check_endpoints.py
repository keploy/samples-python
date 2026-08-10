
import urllib.request
import time
import json
import threading
import sys
import os

# Wait for server to start (manual or automated)
# For this script, we assume the server is running on localhost:5000

BASE_URL = "http://localhost:5000"
ENDPOINTS = [
    '/user/profile',
    '/user/history',
    '/product/search',
    '/admin/config',
    '/data/matrix',
    '/data/mixed_array',
    '/edge/empty_response',
    '/edge/null_root',
    '/edge/large_payload',
    '/edge/special_chars'
]

def check_endpoints():
    print(f"Checking {len(ENDPOINTS)} endpoints on {BASE_URL}...")
    success_count = 0
    fail_count = 0

    for ep in ENDPOINTS:
        url = BASE_URL + ep
        try:
            with urllib.request.urlopen(url) as response:
                status = response.status
                body = response.read().decode('utf-8')
                
                # Basic validation
                if status == 200:
                    print(f"✅ {ep} [200 OK]")
                    # Peek at body if short
                    if len(body) < 100:
                         print(f"   Body: {body}")
                    else:
                         print(f"   Body: {body[:100]}... (truncated)")
                    success_count += 1
                else:
                    print(f"❌ {ep} [{status}]")
                    fail_count += 1
        except Exception as e:
            print(f"❌ {ep} Error: {e}")
            fail_count += 1
            
    print(f"\n--- Summary ---")
    print(f"Total: {len(ENDPOINTS)}")
    print(f"Passed: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    check_endpoints()
