# Progress

## 2026-04-04
- Investigated the xc-cli/FlowDeck eval harness setup and recent runs.
- Confirmed shell scenarios were still inheriting global Droid settings, making shell vs MCP comparisons unfair.
- Confirmed bundled MCP configs still contained machine-specific absolute paths from an older environment.
- Next: isolate Droid settings per trial, make MCP config generation portable, then rerun a focused HackerNews eval slice and inspect any remaining prompt/command-surface gaps.
