# Failure Analysis Report

**Generated**: 2026-04-04  
**Run Directory**: `/Users/james/Developer/zrepos/zmisc/zmirror/xcodebuildmcp_eval/runs/20260404_222447`

## Executive Summary

| Metric | Count |
|--------|-------|
| Total Failures | 2 |
| ENVIRONMENTAL | 2 |
| AGENT_MISTAKE | 0 |
| TASK_ISSUE | 0 |
| UNKNOWN | 0 |

**Key Finding**: All failures in this evaluation run are **ENVIRONMENTAL** and should be **excluded from agent quality analysis**. The agent (droid-minimax) never executed because the evaluation harness passed an invalid empty string for the `--settings` flag, causing immediate startup failure.

### Failures to Exclude from Analysis

| Run ID | Classification | Reason |
|--------|----------------|--------|
| droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775341496427 | ENVIRONMENTAL | Harness misconfiguration |
| droid-minimax-mcp_unprimed-smoke_build_install_launch-trial-1775341501368 | ENVIRONMENTAL | Harness misconfiguration |

---

## Error Themes

### Theme: Harness Configuration Error - Empty Settings Path

- **Classification**: ENVIRONMENTAL
- **Affected runs**: 
  - `droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775341496427`
  - `droid-minimax-mcp_unprimed-smoke_build_install_launch-trial-1775341501368`
- **What happened**: The evaluation harness invoked the `droid` CLI with `--settings ''` (an empty string). The droid CLI requires a valid path for this flag and immediately failed at startup with "Missing value for --settings <path>".

**Example - Actual command executed**:
```
['droid', '--settings', '', 'exec', '--cwd', '/Users/james/.../wt_droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775341496427/ios', '--auto', 'medium', '--output-format', 'json', '--model', 'custom:MiniMax-M2.7-highspeed', '<task prompt>']
```

**Actual error output from transcript**:
```
Startup failed: Missing value for --settings <path>
```

**Why this is ENVIRONMENTAL**:
- The agent never started - it could not have made any mistakes
- Wall time was ~1 second for both runs (just startup + grader check)
- No tool calls were made (tool_error_total = 0 for both)
- No command logs or tool error logs exist (agent never ran)
- This is a harness/infrastructure configuration bug, not agent behavior

---

## Detailed Run Analysis

### droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775341496427

- **Classification**: ENVIRONMENTAL
- **Agent**: droid-minimax
- **Scenario**: shell_unprimed
- **Task**: smoke_build_install_launch
- **Exit Code**: 1
- **Wall Time**: 1.19 seconds
- **Tool Errors**: 0 (agent never ran)

**What went wrong**: Harness passed empty `--settings ''` flag to droid CLI.

**Evidence**:
```
## COMMAND
['droid', '--settings', '', 'exec', ...]

## START 2026-04-04T22:24:58.229821+00:00
## transcript_mode=minimal

Startup failed: Missing value for --settings <path>
```

**Grader result**: `app_not_installed` - expected since the agent never built anything.

---

### droid-minimax-mcp_unprimed-smoke_build_install_launch-trial-1775341501368

- **Classification**: ENVIRONMENTAL  
- **Agent**: droid-minimax
- **Scenario**: mcp_unprimed
- **Task**: smoke_build_install_launch
- **Exit Code**: 1
- **Wall Time**: 1.08 seconds
- **Tool Errors**: 0 (agent never ran)

**What went wrong**: Identical issue - harness passed empty `--settings ''` flag.

**Evidence**:
```
## COMMAND
['droid', '--settings', '', 'exec', ...]

## START 2026-04-04T22:25:02.780203+00:00
## transcript_mode=minimal

Startup failed: Missing value for --settings <path>
```

**Grader result**: `app_not_installed` - expected since the agent never built anything.

---

## Recommendations

### Infrastructure/Harness (Critical)

1. **Fix settings path handling for droid agent**: The harness is passing `--settings ''` (empty string) to the droid CLI. Either:
   - Provide a valid settings file path
   - Omit the `--settings` flag entirely if no settings are needed
   - Handle the case where settings_path is empty/None in the agent configuration

2. **Add startup validation**: Before counting a trial as a "failure", check if the agent actually started. A startup failure should be flagged differently from an agent execution failure.

3. **Log startup failures differently**: Consider adding a `startup_failed` field to run results to distinguish infrastructure failures from agent execution failures.

### Task Definitions

No task definition issues identified - the tasks are reasonable.

### Grading Logic

No grading logic issues identified - the grader correctly reported `app_not_installed` because the app was never built.

### Agent Prompts

Cannot evaluate agent prompt effectiveness since the agent never executed. Re-run after fixing the harness configuration.

---

## Summary

This evaluation run produced **no usable data about agent quality**. Both failures were caused by the same harness misconfiguration bug (empty `--settings` flag). After fixing this infrastructure issue, the evaluation should be re-run to obtain valid results for comparing the droid-minimax agent across shell_unprimed and mcp_unprimed scenarios.
