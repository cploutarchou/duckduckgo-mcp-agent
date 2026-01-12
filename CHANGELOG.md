# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-01-12
### Added
- Expose DuckDuckGo tuning parameters in `web_search`: `region`, `safesearch`, `timelimit`.
- Improved result formatting to Markdown links with snippets.
- Surface app version in MCP `initialize` response.

### Changed
- Bump `duckduckgo-search` to `>=8.3.0` in requirements.

### Fixed
- Preserve guard for known `duckduckgo_search` TypeError and add fallback when signature differs.

---

## [1.0.0] - 2025-xx-xx
- Initial release with minimal MCP HTTP SSE server and DuckDuckGo search tool.
