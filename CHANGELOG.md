# Changelog

All notable changes to this project will be documented in this file.

## [1.2.1] - 2026-01-12
### Added
- Result deduplication to eliminate duplicate URLs
- Domain extraction for each result (📍 indicator)
- Improved result formatting with better Markdown presentation

### Fixed
- Filter out results with missing titles or snippets
- Truncate long snippets to 200 characters for readability
- Clean extra whitespace in result text
- **Suppress verbose INFO logs from ddgs, primp, httpx libraries** (reduces log noise)
- **Improve network/DNS error handling** (gracefully handle connectivity issues in containerized environments)
- **Reduce log verbosity for request cancellations** (normal client operations, not errors)

### Changed
- Enhanced search result response header with query display

---

## [1.2.0] - 2026-01-12
### Added
- `all_results` flag for `web_search` to fetch larger result sets (internal safety cap of 100).
- Version bump surfaced in initialize.

### Changed
- Docs updated for new flag and examples.

---

## [1.1.0] - 2026-01-12
### Added
- Expose DuckDuckGo tuning parameters in `web_search`: `region`, `safesearch`, `timelimit`.
- Improved result formatting to Markdown links with snippets.
- Surface app version in MCP `initialize` response.

### Changed
- Bump `duckduckgo-search` to a version supporting params.

### Fixed
- Preserve guard for known `duckduckgo_search` TypeError and add fallback when signature differs.

---

## [1.0.0] - 2025-xx-xx
- Initial release with minimal MCP HTTP SSE server and DuckDuckGo search tool.
