# Tool Error Report

**Run:** 2026-04-04T19:21:57  
**Agent:** codex | **Scenario:** shell_primed | **Task:** smoke_build_install_launch  
**Error Rate:** 100% (1/1 runs with errors)

## Summary

All 3 errors are non-MCP bash failures from the codex agent attempting to use a shell-based `xc` CLI tool that is not available in this environment. The agent should have used MCP tools exclusively.

## Error Details

| Time | Exit Code | Failed Command (inferred) | Follow-up Action |
|------|-----------|---------------------------|------------------|
| 19:26:55 | 1 | Unknown bash command | Agent ran `pwd`, `rg --files` - **pivoted to exploration** |
| 19:28:09 | 5 | Likely `xc` command | Agent tried `xc help apps`, `xc dev launch --help` - **sought documentation** |
| 19:31:13 | 64 | `xc` command (usage error) | Agent tried `xc dev launch --help`, then `xc status --json \| rg ...` - **still using unavailable tool** |

## Analysis

### Agent Mistakes (Likely)
- **Wrong tool selection**: Agent used shell `xc` CLI wrapper instead of available MCP tools. The MCP command log shows correct `xcodebuild`/`xcrun` calls via MCP were working successfully throughout the run.
- **Persistence on failing approach**: After exit code 5 (command not found / tool error), agent continued attempting `xc` variants rather than switching to the working MCP tools.

### Correction Behavior
- Agent changed parameters between errors (exploring help/docs), showing some adaptation.
- However, agent never corrected the fundamental issue of using the wrong tool category.

## Recommendations

1. **Priming/scenario config**: Ensure `shell_primed` scenario either provides the `xc` CLI or explicitly instructs agent to use MCP tools only.
2. **Agent prompt tuning**: Reinforce MCP-first approach when MCP tools are available; shell fallback should be last resort.

---
*3 real errors | 0 MCP errors | 0 transient/environmental failures*
