# Tool Error Report

**Run:** 2026-04-04T20:10:20Z  
**Total Runs:** 2 | **Runs with Errors:** 1 (50%)

## Summary by Agent

| Agent | Trials | Errors | Error Type |
|-------|--------|--------|------------|
| codex | 1 | 6 | bash (non-MCP) |
| droid-minimax | 1 | 0 | — |

## Error Analysis: codex / shell_primed

**Task:** smoke_build_install_launch  
**6 consecutive bash failures** — all related to `xc` CLI misuse.

### Error Sequence

| # | Exit | Command | Classification |
|---|------|---------|----------------|
| 1 | 2 | `xc help project --json` | Agent mistake — invalid help syntax |
| 2 | 2 | `xc help apps --json` | Agent mistake — invalid help syntax |
| 3 | 70 | `xc project --json` | Agent mistake — missing context/args |
| 4 | 5 | (xc subcommand) | Likely CLI error |
| 5 | 1 | `pgrep -af '...'` | Benign — no matching processes found |
| 6 | -1 | `xc dev run ... --json` | Timeout or signal |

### Correction Behavior

**One correction attempt observed:**  
After error #6 (`xc dev run ... --json` failed with exit -1), agent retried with `--no-console` flag added — indicates adaptive behavior, but too late in the sequence.

**No corrections for early errors:**  
Errors 1-3 show the agent probing `xc help <topic>` syntax incorrectly multiple times without adjusting approach. Agent moved on rather than fixing the pattern.

## Conclusions

| Category | Count | Notes |
|----------|-------|-------|
| **Agent mistakes** | 4 | Incorrect `xc` CLI syntax (help subcommands, missing args) |
| **Benign/expected** | 1 | `pgrep` exit 1 = no matches |
| **Environmental** | 1 | Exit -1 suggests timeout or process interruption |

### Actionable Items

1. **Codex needs `xc` CLI priming** — agent does not know valid `xc` subcommand syntax; consider adding CLI reference to system prompt for shell_primed scenario
2. **Help exploration pattern is wasteful** — 3 consecutive failures probing help topics; agent should fallback to `xc --help` or documentation faster
3. **droid-minimax succeeded** — compare approaches to identify what codex missed
