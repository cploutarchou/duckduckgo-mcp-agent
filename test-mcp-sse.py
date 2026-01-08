#!/usr/bin/env python3
"""Test MCP server SSE responses."""

import json
import sys
import urllib.request


def test_mcp_endpoint(method: str, params: dict = None):
    """Test an MCP endpoint and print the SSE stream."""
    url = "http://127.0.0.1:8000/"
    payload = {"method": method}
    if params:
        payload["params"] = params

    print(f"\n{'=' * 60}")
    print(f"Testing: {method}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'=' * 60}\n")

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Status Code: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}\n")

            # Read and print SSE stream
            print("SSE Stream:")
            print("-" * 60)
            content = response.read().decode("utf-8")
            print(content)
            print("-" * 60)

            return True

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    tests = [
        (
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        ),
        ("tools/list", None),
        (
            "tools/call",
            {
                "name": "web_search",
                "arguments": {"query": "Python programming", "max_results": 3},
            },
        ),
        ("invalid_method", None),  # Test error handling
    ]

    results = []
    for method, params in tests:
        success = test_mcp_endpoint(method, params)
        results.append((method, success))
        print()

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    for method, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {method}")

    # Exit with error code if any test failed
    if not all(success for _, success in results):
        sys.exit(1)
