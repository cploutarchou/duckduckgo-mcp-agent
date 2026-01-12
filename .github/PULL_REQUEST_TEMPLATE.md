## Summary

- Improves DuckDuckGo search results by exposing tuning parameters (`region`, `safesearch`, `timelimit`).
- Better markdown formatting of results.
- Bumps dependency and versions the app.

## Changes

- Add APP_VERSION and surface in `initialize`.
- Extend `tools/list` schema.
- Update `tools/call` search logic with validated params and fallback for library quirks.
- Update README and CHANGELOG.

## Testing

- Run `make run-dev` then `python test-mcp-sse.py`.
- Example JSON-RPC payload:
```
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"web_search","arguments":{"query":"fastapi sse","max_results":5,"region":"us-en","safesearch":"moderate","timelimit":"w"}}}
```

## Checklist
- [ ] Linted and formatted
- [ ] Tested locally
- [ ] Single-file design preserved
