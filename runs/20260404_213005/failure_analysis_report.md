# Failure Analysis Report

## Executive Summary

- **Total failures**: 2
- **Breakdown by classification**:
  - ENVIRONMENTAL: 2 (100%)
  - AGENT_MISTAKE: 0
  - TASK_ISSUE: 0
  - UNKNOWN: 0

**Key finding**: All failures in this evaluation run are ENVIRONMENTAL. The agent CLI failed to start due to a model configuration issue. The agent never executed any task logic.

**Failures to exclude from agent quality analysis**: Both failures should be excluded since they reflect infrastructure/configuration issues, not agent capabilities.

---

## Error Themes

### Theme: Model Configuration Failure

- **Classification**: ENVIRONMENTAL
- **Affected runs**:
  - `droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775338212529`
  - `droid-minimax-shell_primed-smoke_build_install_launch-trial-1775338218516`
- **What happened**: The evaluation harness invoked the "droid" CLI with `--model "MiniMax-M2.7 Highspeed"`, but the CLI rejected this model name as invalid and exited immediately without starting the agent.

- **Evidence from transcript**:
```
Invalid model: MiniMax-M2.7 Highspeed
Available built-in models:
claude-opus-4-5-20251101, claude-opus-4-6, claude-opus-4-6-fast, claude-sonnet-4-5-20250929, claude-sonnet-4-6, claude-haiku-4-5-20251001, gpt-5.2, gpt-5.2-codex, gpt-5.4, gpt-5.4-fast, gpt-5.4-mini, gpt-5.3-codex, gpt-5.3-codex-fast, gemini-3.1-pro-preview, gemini-3-flash-preview, glm-4.7, glm-5, kimi-k2.5, minimax-m2.5, gpt-5.1-codex-max
Available custom models:
Opus 4.6, Opus 4.6 (Thinking), GPT-5.4 (Priority), GPT-5.4 (Default), GPT-5.4 high (Default), GPT-5.4 high (Priority), GPT-5.4 xhigh (Default), GPT-5.4 xhigh (Priority), GPT-5.4 (Flex), MiniMax-M2.7 Highspeed, OpenRouter GPT-5.4-mini, OpenRouter xiaomi
Note: Custom models are loaded from ~/.factory/settings.json
```

- **Paradox observed**: The model "MiniMax-M2.7 Highspeed" appears in the "Available custom models" list, yet the CLI reports it as invalid. This suggests either:
  1. A case-sensitivity or whitespace matching issue in the CLI's model validation
  2. A race condition or configuration loading issue
  3. The custom model definition in `~/.factory/settings.json` is malformed or incomplete

- **Impact**: 
  - Agent never started
  - No tool calls were made
  - Wall time was ~2 seconds (immediate failure)
  - No command logs exist (agent never executed commands)

---

## Detailed Run Analysis

### droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775338212529

- **Classification**: ENVIRONMENTAL
- **Agent/Scenario/Task**: droid-minimax / shell_unprimed / smoke_build_install_launch
- **What went wrong**: CLI model validation rejected the configured model before agent could start
- **Evidence**: 
  - Wall time: 1.82s (immediate exit)
  - Exit code: 1
  - Transcript shows CLI error output, no agent reasoning or tool calls
  - No cmd_log.jsonl file created (agent never ran)
  - tool_error_total: 0 (no tool calls attempted)
- **Command attempted**:
```
droid exec --cwd <worktree>/ios --auto medium --output-format json --model "MiniMax-M2.7 Highspeed" "<prompt>"
```

### droid-minimax-shell_primed-smoke_build_install_launch-trial-1775338218516

- **Classification**: ENVIRONMENTAL
- **Agent/Scenario/Task**: droid-minimax / shell_primed / smoke_build_install_launch
- **What went wrong**: Identical to above - CLI model validation failure
- **Evidence**:
  - Wall time: 2.22s (immediate exit)
  - Exit code: 1
  - Transcript shows same CLI error pattern
  - No cmd_log.jsonl file created
  - tool_error_total: 0 (no tool calls attempted)
- **Note**: Even though this scenario provided build parameters (project, scheme, bundle_id, etc.) in the prompt, the agent never got a chance to use them.

---

## Recommendations

### Infrastructure/Harness
1. **Fix model name validation**: Investigate why "MiniMax-M2.7 Highspeed" is listed in custom models but fails validation. Check for:
   - Case sensitivity issues
   - Trailing/leading whitespace in the settings.json model name
   - Model alias vs model ID mismatch
   
2. **Pre-flight validation**: Add a harness check that verifies the configured model is actually usable before starting a trial. This would fail fast with a clear error rather than creating failed trial records.

3. **Retry or skip**: Consider adding logic to skip or mark as "harness_error" when the agent CLI fails at startup rather than recording it as a task failure.

### Task Definitions
- No issues identified - the task definitions were not reached.

### Grading Logic
- Consider adding a "harness_error" or "agent_not_started" failure category distinct from "app_not_installed" to make filtering easier.

### Agent Prompts
- No issues identified - the agent never received the prompts.

---

## Summary Table

| Run ID | Agent | Scenario | Classification | Root Cause |
|--------|-------|----------|----------------|------------|
| droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775338212529 | droid-minimax | shell_unprimed | ENVIRONMENTAL | Model config invalid |
| droid-minimax-shell_primed-smoke_build_install_launch-trial-1775338218516 | droid-minimax | shell_primed | ENVIRONMENTAL | Model config invalid |

---

## Conclusion

**100% of failures in this evaluation run should be excluded from agent quality analysis.** Both failures were caused by a harness/infrastructure configuration issue where the "droid" CLI could not recognize the "MiniMax-M2.7 Highspeed" model, despite it appearing in the available custom models list.

The agent never started, made no decisions, called no tools, and executed no commands. These failures tell us nothing about the agent's ability to build, install, and launch iOS apps - they only reveal a model configuration bug in the evaluation infrastructure.
