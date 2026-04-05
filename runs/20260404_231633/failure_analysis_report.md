# Failure Analysis Report

**Run Directory:** `/Users/james/Developer/zrepos/zmisc/zmirror/xcodebuildmcp_eval/runs/20260404_231633`  
**Generated:** 2026-04-04  
**Total Failures:** 1

## Executive Summary

| Classification | Count | Should Exclude from Agent Quality Analysis? |
|---------------|-------|---------------------------------------------|
| AGENT_MISTAKE | 1     | No - reflects agent behavior                |
| ENVIRONMENTAL | 0     | N/A                                         |
| TASK_ISSUE    | 0     | N/A                                         |
| UNKNOWN       | 0     | N/A                                         |

**Key Finding:** The single failure is an AGENT_MISTAKE where the agent successfully completed the task (build, install, launch all verified by graders) but failed to exit, causing a timeout. This reflects agent behavior, not infrastructure issues.

**Recommendation:** No failures should be excluded from agent quality analysis in this run.

## Error Themes

### Theme: Agent Did Not Exit After Success

- **Classification**: AGENT_MISTAKE
- **Affected runs**: `droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775344617168`
- **What happened**: The agent successfully built, installed, and launched the app (both graders returned `ok: true`), but did not terminate. The agent continued running until it hit the 8-minute hard timeout.

**Evidence from grader results:**
```json
"grader_results": [
  {"type": "ios_install_check", "ok": true, "reason": null, "duration_sec": 0.759},
  {"type": "ios_launch_check", "ok": true, "reason": null, "duration_sec": 0.872}
]
```

**Timeline from command log:**
| Time | Action |
|------|--------|
| 23:17:02 | Run started |
| 23:17:15 | First xcodebuild -list |
| 23:18:15 | Build started |
| 23:19:11 | Build completed |
| 23:20:34 | **App launched successfully** (final command) |
| 23:25:04 | **Timeout after 480s** (4.5 minutes of inactivity) |

The agent's final command was the successful launch:
```
xcrun simctl launch \
  --stdout=/var/folders/x7/.../stdout.log \
  --stderr=/var/folders/x7/.../stderr.log \
  BEDDE8E2-8D1C-4730-B7E6-AE8F163759AB \
  com.emergetools.hackernews
```

After this command, the agent did not exit for 4.5 minutes until the hard timeout killed the process.

**Task instructions were clear:**
> "When you believe it is successful, exit immediately."
> "Exit immediately after the success criteria are met; do not keep exploring once install+launch succeeds."

**Additional inefficiencies observed:**
- `xcodebuild_repeat_count: 6` - redundant project inspection calls
- Two different simulator UDIDs used (FA553193... then BEDDE8E2...) despite instruction to "resolve the exact UDID... and reuse that same UDID throughout"
- `time_to_first_xcodebuild_sec: 78.1` - took over a minute before first build attempt

## Detailed Run Analysis

### droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775344617168

| Field | Value |
|-------|-------|
| **Classification** | AGENT_MISTAKE |
| **Agent** | droid-minimax (MiniMax-M2.7-highspeed) |
| **Scenario** | shell_unprimed |
| **Task** | smoke_build_install_launch |
| **Exit Code** | 124 (timeout) |
| **Wall Time** | 480.08s (full timeout) |
| **Tool Errors** | 0 |

**What went wrong:**

The agent completed the task successfully but did not exit. The model (MiniMax-M2.7-highspeed) appears to have either:
1. Not recognized that the task was complete
2. Not known how to signal completion/exit
3. Been waiting for some other event that never occurred

The transcript shows `transcript_mode=minimal`, so detailed agent reasoning is not available. However, the command log shows no commands were issued after the successful launch at 23:20:34, indicating the agent was idle or thinking for the remaining 4.5 minutes.

**Commands executed (chronological):**
```
1. xcodebuild -project HackerNews.xcodeproj -list -json
2. xcrun simctl list devices available
3. xcodebuild -project HackerNews.xcodeproj -list -json  (repeat)
4. xcodebuild -project HackerNews.xcodeproj -list -json  (repeat)
5. xcodebuild ... -showdestinations
6. xcrun simctl list devices --json
7. xcodebuild build -destination id=BEDDE8E2...  (BUILD 1)
8. xcrun xcresulttool get object ...
9. xcrun simctl list devices --json
10. xcrun simctl boot FA553193...
11. xcrun simctl bootstatus FA553193... -b
12. xcrun simctl list devices --json
13. xcrun simctl list devices --json  (repeat)
14. xcrun simctl spawn FA553193... log stream ...
15. xcrun simctl install FA553193... HackerNews.app  (INSTALL 1 - wrong device?)
16. xcodebuild -project HackerNews.xcodeproj -list -json  (repeat)
17. xcodebuild -project HackerNews.xcodeproj -list -json  (repeat)
18. xcodebuild ... -showdestinations
19. xcrun simctl list devices --json
20. xcodebuild build -destination id=BEDDE8E2...  (BUILD 2 - rebuild)
21. xcrun xcresulttool get object ...
22. xcrun simctl list devices --json
23. xcrun simctl list devices --json  (repeat)
24. xcrun simctl spawn BEDDE8E2... log stream ...
25. xcrun simctl install BEDDE8E2... HackerNews.app  (INSTALL 2)
26. xcrun simctl launch BEDDE8E2... com.emergetools.hackernews  (LAUNCH - SUCCESS)
--- 4.5 minutes of no activity until timeout ---
```

**Key observations:**
- Agent installed on FA553193... first, then rebuilt and installed on BEDDE8E2...
- Multiple redundant `xcodebuild -list` calls (6 total)
- Agent did get the task done, just didn't exit

## Recommendations

### Agent Prompts
1. **Stronger exit instructions for MiniMax model**: The current prompt says to "exit immediately" after success, but the MiniMax-M2.7-highspeed model did not comply. Consider adding more explicit termination instructions or testing whether this model has different exit/completion semantics.

2. **Success verification step**: Consider adding instructions like "After launch succeeds, verify success by checking the app is running, then immediately exit with success code."

### Infrastructure/Harness
1. **Soft timeout with success check**: Consider adding a soft timeout that checks grader status mid-run. If both graders pass but agent is still running, the harness could either:
   - Mark as success despite timeout (since task was actually completed)
   - Send a signal to the agent to terminate

2. **Idle detection**: If an agent issues no commands for >60 seconds after a launch command succeeds, consider proactively terminating with a special exit code.

### Task Definitions
1. No changes needed - the task instructions were clear and correct. The agent simply didn't follow them.

### Grading Logic
1. Consider a "success_despite_timeout" outcome for cases where:
   - All graders pass
   - Failure reason is only "timeout_hard"
   - Agent completed the functional requirements but failed to exit

   This would allow distinguishing between "agent too slow to complete" vs "agent completed but didn't exit."

## Appendix: Raw Failure Data

```json
{
  "run_id": "droid-minimax-shell_unprimed-smoke_build_install_launch-trial-1775344617168",
  "agent_id": "droid-minimax",
  "scenario": "shell_unprimed", 
  "task_id": "smoke_build_install_launch",
  "success": false,
  "failure_reason": "timeout_hard",
  "exit_code": 124,
  "wall_time_sec": 480.08,
  "grader_results": [
    {"type": "ios_install_check", "ok": true},
    {"type": "ios_launch_check", "ok": true}
  ],
  "tool_error_total": 0,
  "xcodebuild_calls": 9,
  "xcrun_calls": 17,
  "simctl_calls": 15,
  "xcodebuild_repeat_count": 6,
  "time_to_first_xcodebuild_sec": 78.14
}
```
