# Failure Analysis Report

## Executive Summary

| Metric | Value |
|--------|-------|
| Total failures | 2 |
| ENVIRONMENTAL | 2 (100%) |
| AGENT_MISTAKE | 0 |
| TASK_ISSUE | 0 |
| UNKNOWN | 0 |

**Key Finding**: All 2 failures in this evaluation run are ENVIRONMENTAL - caused by an invalid model configuration in the harness. The agent (`droid-minimax`) never executed because the model name `custom:MiniMax-M2.7-5` does not exist.

**Failures to exclude from agent quality analysis**: ALL 2 failures should be excluded. These do not reflect agent capabilities - the agent never had a chance to run.

## Error Themes

### Theme: Invalid Model Configuration

- **Classification**: ENVIRONMENTAL
- **Affected runs**: 
  - `droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775338084290`
  - `droid-minimax-shell_primed-smoke_build_install_launch-trial-1775338120264`
- **What happened**: The evaluation harness invoked the `droid` CLI with an invalid model name. The model `custom:MiniMax-M2.7-5` does not exist in the available model list. The agent immediately failed to start - no tool calls, no commands, no work was performed.

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
Note: Custom models are loaded from ~/.factory/settings.json
```

**Probable cause**: The harness configuration uses `custom:MiniMax-M2.7-5` but the actual custom model name is `MiniMax-M2.7 Highspeed`. This could be:
1. A typo in the agent configuration (`MiniMax-M2.7-5` vs `MiniMax-M2.7 Highspeed`)
2. A model rename that wasn't reflected in the eval config
3. An incorrect model identifier format (should use exact name, not partial)

## Detailed Run Analysis

### droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775338084290

| Field | Value |
|-------|-------|
| **Classification** | ENVIRONMENTAL |
| **Agent** | droid-minimax |
| **Scenario** | shell_unprimed |
| **Task** | smoke_build_install_launch |
| **Wall time** | 5.87s |
| **Exit code** | 1 |
| **Tool errors** | 0 (agent never started) |

**What went wrong**: The harness attempted to start the `droid` CLI with `--model custom:MiniMax-M2.7-5`. This model does not exist. The CLI printed an error message listing available models and exited with code 1. The agent never executed any commands or tool calls.

**Command invoked**:
```
droid exec --cwd <worktree>/ios --auto medium --output-format json --model custom:MiniMax-M2.7-5 "<prompt>"
```

**Why "app_not_installed"**: The grader ran after the harness exited and found no app installed on the simulator - because no build/install commands were ever executed.

---

### droid-minimax-shell_primed-smoke_build_install_launch-trial-1775338120264

| Field | Value |
|-------|-------|
| **Classification** | ENVIRONMENTAL |
| **Agent** | droid-minimax |
| **Scenario** | shell_primed |
| **Task** | smoke_build_install_launch |
| **Wall time** | 2.17s |
| **Exit code** | 1 |
| **Tool errors** | 0 (agent never started) |

**What went wrong**: Identical to the previous run - invalid model configuration. The only difference is this was the `shell_primed` scenario (build params provided in prompt), but it made no difference since the agent never started.

## Recommendations

### Immediate Fix Required

1. **Fix the model configuration**: Update the `droid-minimax` agent configuration to use a valid model name. Based on the available models list, the correct value should likely be one of:
   - `minimax-m2.5` (built-in)
   - `MiniMax-M2.7 Highspeed` (custom, via `custom:MiniMax-M2.7 Highspeed`)

### Harness Improvements

2. **Validate model names before running**: The harness should validate that the configured model exists before starting a trial. This would fail fast with a clear error message rather than creating failed trial data.

3. **Log harness errors separately from agent failures**: When the agent CLI fails to start (exit code 1 with no transcript content), this should be flagged as a harness/configuration error, not an agent failure. Consider adding a `harness_error` status distinct from `success: false`.

4. **Re-run the evaluation**: These 2 runs should be re-executed with a valid model configuration to get meaningful results for the `droid-minimax` agent.

### No Agent/Task Changes Needed

Since the agent never executed, there is no feedback on:
- Agent behavior or tool-calling patterns
- Task definition quality
- Grading logic accuracy

All analysis of the `droid-minimax` agent should wait until valid runs are collected.
