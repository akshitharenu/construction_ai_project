#!/usr/bin/env python3
"""Comprehensive API endpoint tests"""
import urllib.request
import json

base_url = "http://localhost:8000"
tests = [
    ("GET", "/health", None),
    ("GET", "/debug", None),
    ("GET", "/stats/PROJ-001", None),
    ("POST", "/report/generate", {"project_id": "PROJ-001"}),
    ("POST", "/update", {"content": "Test site update", "source": "api", "sender": "test_user"}),
]

print("=" * 60)
print("CONSTRUCTION AI - ENDPOINT TESTS")
print("=" * 60)

for method, endpoint, payload in tests:
    try:
        url = f"{base_url}{endpoint}"
        if method == "GET":
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                print(f"\n✓ {method:4} {endpoint:25} SUCCESS")
                print(f"  Response: {json.dumps(result, indent=2)[:150]}...")
        else:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method=method
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                print(f"\n✓ {method:4} {endpoint:25} SUCCESS")
                print(f"  Response: {json.dumps(result, indent=2)[:150]}...")
    except Exception as e:
        print(f"\n✗ {method:4} {endpoint:25} FAILED")
        print(f"  Error: {type(e).__name__}: {str(e)[:80]}")

print("\n" + "=" * 60)
print("TESTS COMPLETED")
print("=" * 60)
