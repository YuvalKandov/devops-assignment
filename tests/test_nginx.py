#!/usr/bin/env python3
"""
Test script for Nginx container.
Verifies HTTPS responses, error responses, and rate limiting behavior.
"""
import os
import ssl
import sys
import time
import threading
import urllib.request
import urllib.error

# Get nginx host from environment
NGINX_HOST = os.getenv("NGINX_HOST", "localhost")


def fetch(url, timeout=5):
    """Fetch a URL and return (status_code, body). Handles HTTPS with self-signed certs."""
    ctx = None
    if url.startswith("https://"):
        ctx = ssl._create_unverified_context()

    req = urllib.request.Request(url, headers={"User-Agent": "nginx-tester"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = ""
        if e.fp:
            body = e.fp.read().decode("utf-8", errors="replace")
        return e.code, body
    except Exception as e:
        return None, str(e)


def test_https_success():
    """Test that HTTPS port 8443 returns 200 OK with expected content."""
    url = f"https://{NGINX_HOST}:8443"
    status, body = fetch(url)

    assert status == 200, f"Expected 200, got {status}"
    assert "Hello from Nginx" in body, "Expected content not found"
    print("✓ HTTPS 200 test passed")


def test_http_error():
    """Test that port 8081 returns 404 Not Found."""
    url = f"http://{NGINX_HOST}:8081"
    status, body = fetch(url)

    assert status == 404, f"Expected 404, got {status}"
    print("✓ HTTP 404 test passed")


def test_rate_limiting():
    """
    Test rate limiting by sending requests faster than 5/second.
    Expected: Some requests should return 429 Too Many Requests.
    Uses retry logic to handle timing variability.
    """
    url = f"https://{NGINX_HOST}:8443"

    def make_concurrent_requests(num_requests=30):
        """Send concurrent requests and return list of status codes."""
        results = []
        lock = threading.Lock()

        def worker():
            status, _ = fetch(url, timeout=5)
            with lock:
                results.append(status)

        threads = [threading.Thread(target=worker) for _ in range(num_requests)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return results

    # Retry up to 5 times
    for attempt in range(5):
        results = make_concurrent_requests(30)
        rate_limited = results.count(429)

        if rate_limited > 0:
            print(f"✓ Rate limiting test passed ({rate_limited}/30 requests were rate limited)")
            return

        time.sleep(1)

    # If we get here, no 429s were observed in any attempt
    assert False, f"Expected some 429 responses after 5 attempts, got none. Last results: {results}"


def main():
    """Run all tests."""
    tests = [
        test_https_success,
        test_http_error,
        test_rate_limiting,
    ]

    failed = False
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed = True
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed = True

    if failed:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
