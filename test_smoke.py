#!/usr/bin/env python3
import json
import sys
import time
import urllib.error
import urllib.request

PORT = 8002
URL = f"http://127.0.0.1:{PORT}/"


def post(payload: dict, timeout=10) -> str:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def wait_server(retries=20, delay=0.25) -> bool:
    for _ in range(retries):
        try:
            _ = post({"method": "initialize", "id": 1, "jsonrpc": "2.0"}, timeout=3)
            return True
        except Exception:
            time.sleep(delay)
    return False


def main() -> int:
    if not wait_server():
        print("❌ Server not responding on", URL)
        return 1

    init = post({"method": "initialize", "id": 1, "jsonrpc": "2.0"})
    if "event: message" not in init or "event: done" not in init:
        print("❌ Initialize SSE format check failed\n", init)
        return 1

    search = post(
        {
            "method": "tools/call",
            "id": 2,
            "jsonrpc": "2.0",
            "params": {
                "name": "web_search",
                "arguments": {"query": "fastapi", "max_results": 1},
            },
        }
    )
    if "event: message" not in search or "event: done" not in search:
        print("❌ tools/call SSE format check failed\n", search)
        return 1

    print("✅ Smoke tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
