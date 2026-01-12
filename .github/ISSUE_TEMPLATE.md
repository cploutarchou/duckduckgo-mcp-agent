## Feature request: Improve DuckDuckGo search results

### Summary
Expose and document tuning parameters for DuckDuckGo search to improve relevance and control.

### Acceptance Criteria
- `web_search` supports optional `region`, `safesearch`, `timelimit` parameters
- Input schema updated in `tools/list`
- Results formatted as markdown links
- Maintain single-file architecture and SSE behavior
- Preserve known error guards for `duckduckgo_search`

### Notes
- Reference: https://pypi.org/project/duckduckgo-search/
- Cap `max_results` at 20 as before
