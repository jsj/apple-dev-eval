# Failure Analysis Report

**Generated**: 2026-04-04  
**Run Directory**: `/Users/james/Developer/zrepos/zmisc/zmirror/xcodebuildmcp_eval/runs/20260404_200623`

## Executive Summary

| Classification | Count | % of Failures |
|----------------|-------|---------------|
| ENVIRONMENTAL  | 1     | 100%          |
| AGENT_MISTAKE  | 0     | 0%            |
| TASK_ISSUE     | 0     | 0%            |
| UNKNOWN        | 0     | 0%            |

**Total Failures**: 1

**Key Finding**: The single failure in this evaluation run was entirely ENVIRONMENTAL - an invalid model configuration prevented the agent from starting. **This failure should be excluded from agent quality analysis** as it reflects a harness/infrastructure issue, not agent behavior.

No agent mistakes were observed because the agent never executed any actions.

---

## Error Themes

### Theme: Invalid Model Configuration

- **Classification**: ENVIRONMENTAL
- **Affected runs**: `droid-minimax-shell_primed-smoke_build_install_launch-trial-1775333191449`
- **What happened**: The evaluation harness attempted to invoke the agent with model `custom:MiniMax-M2.7-5`, which does not exist in the available models. The agent CLI immediately rejected the request and terminated without executing any agent logic.

**Evidence from transcript**:
```
Invalid model: custom:MiniMax-M2.7-5
Available built-in models:
claude-opus-4-5-20251101, claude-opus-4-6, claude-opus-4-6-fast, claude-sonnet-4-5-20250929, 
claude-sonnet-4-6, claude-haiku-4-5-20251001, gpt-5.2, gpt-5.2-codex, gpt-5.4, gpt-5.4-fast, 
gpt-5.4-mini, gpt-5.3-codex, gpt-5.3-codex-fast, gemini-3.1-pro-preview, gemini-3-flash-preview, 
glm-4.7, glm-5, kimi-k2.5, minimax-m2.5, gpt-5.1-codex-max
Available custom models:
Opus 4.6, Opus 4.6 (Thinking), GPT-5.4 (Priority), GPT-5.4 (Default), GPT-5.4 high (Default), 
GPT-5.4 high (Priority), GPT-5.4 xhigh (Default), GPT-5.4 xhigh (Priority), GPT-5.4 (Flex), 
MiniMax-M2.7 Highspeed, OpenRouter GPT-5.4-mini, OpenRouter xiaomi
```

**The command that failed**:
```bash
droid exec --cwd /Users/james/.../ios --auto medium --output-format json \
  --model custom:MiniMax-M2.7-5 "You are working in a local iOS repo..."
```

**Root cause**: The model identifier `custom:MiniMax-M2.7-5` does not match any available model. The closest matches are:
- Built-in: `minimax-m2.5`
- Custom: `MiniMax-M2.7 Highspeed`

The error appeared twice in the transcript, suggesting the harness may have retried the failed command once.

---

## Detailed Run Analysis

### droid-minimax-shell_primed-smoke_build_install_launch-trial-1775333191449

| Field | Value |
|-------|-------|
| **Classification** | ENVIRONMENTAL |
| **Agent** | droid-minimax |
| **Scenario** | shell_primed |
| **Task** | smoke_build_install_launch |
| **Wall Time** | 3.95 seconds |
| **Exit Code** | 1 |
| **Failure Reason** | app_not_installed |
| **Tool Errors** | 0 (agent never ran) |

**What went wrong**: The evaluation harness could not start the agent due to an invalid model identifier in the configuration. The model `custom:MiniMax-M2.7-5` is not defined in either built-in models or `~/.factory/settings.json` custom models.

**Why this is ENVIRONMENTAL, not AGENT_MISTAKE**:
- The agent never executed a single tool call or command
- The agent never had an opportunity to attempt the task
- The failure occurred before any agent logic ran
- This is a configuration/infrastructure mismatch

**Evidence**:
- `tool_error_total: 0` - No tool errors because no tools were called
- `wall_time_sec: 3.95` - Very short runtime, consistent with immediate failure
- Transcript shows only model validation errors, no agent actions
- No `cmd_log.jsonl` or `tool_errors.jsonl` files exist (agent never ran)

---

## Recommendations

### Infrastructure/Harness
1. **Validate model configurations before running trials**: The harness should verify that configured model identifiers exist before attempting to run evaluations. This would fail fast with a clear error rather than recording a confusing "app_not_installed" failure.

2. **Fix the MiniMax model identifier**: Update the agent configuration to use either:
   - `minimax-m2.5` (built-in)
   - `MiniMax-M2.7 Highspeed` (custom, if this is the intended model)
   
   The current `custom:MiniMax-M2.7-5` appears to be a typo or outdated reference.

3. **Distinguish harness failures from agent failures**: When the agent CLI exits with an error before running (e.g., invalid model, missing credentials), the harness should mark the failure reason as `harness_error` or similar, not `app_not_installed` which implies the agent tried but failed to install the app.

### Task Definitions
- No issues identified (task never executed).

### Grading Logic
- Consider adding a check for agent transcript length or tool call count. A run with 0 tool calls and < 5 seconds runtime that fails should be flagged as a potential infrastructure issue.

### Agent Prompts
- No issues identified (agent never received the prompt).

---

## Summary Table

| Run ID | Classification | Agent | Scenario | Task | Failure Reason | Notes |
|--------|----------------|-------|----------|------|----------------|-------|
| droid-minimax-shell_primed-smoke_build_install_launch-trial-1775333191449 | ENVIRONMENTAL | droid-minimax | shell_primed | smoke_build_install_launch | Invalid model config | Model `custom:MiniMax-M2.7-5` does not exist |

---

## Appendix: Runs to Exclude from Agent Quality Analysis

The following runs should be **excluded** from any analysis measuring agent quality, success rates, or capabilities:

1. `droid-minimax-shell_primed-smoke_build_install_launch-trial-1775333191449` - Agent never started due to invalid model configuration

**Net effect**: After excluding environmental failures, this evaluation run has **0 failures** attributable to agent behavior.
