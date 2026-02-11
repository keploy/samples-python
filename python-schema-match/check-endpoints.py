import urllib.request
import time
import sys

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
    '/edge/special_chars',
    '/edge/nested_null',
    '/complex/user',
    '/complex/product'
]

def check_endpoints():
    print(f"Checking {len(ENDPOINTS)} endpoints on {BASE_URL}...")
    success_count = 0
    fail_count = 0

    for ep in ENDPOINTS:
        url = BASE_URL + ep
        try:
            # Short timeout to fail fast
            with urllib.request.urlopen(url, timeout=2) as response:
                status = response.status
                body = response.read().decode('utf-8')
                
                if status == 200:
                    print(f"✅ {ep} [200 OK]")
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
    # Small delay to ensure server is ready
    time.sleep(2)
    check_endpoints()