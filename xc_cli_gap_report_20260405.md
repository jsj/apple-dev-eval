# xc-cli benchmark gap report

Run analyzed: `/Users/james/Developer/zrepos/zmisc/zmirror/xcodebuildmcp_eval/runs/20260405_014518`
Config used: `config_droid_gpt54_shell.yaml`
Scenario: `shell_primed`
Agent: `droid-gpt54`
Trials per task: `1`

## Executive summary

The run finished with **0/5 task success** but the dominant failures are **eval-environment / harness compatibility issues**, not clean evidence that `xc-cli` itself is missing core functionality.

There are three separate gap buckets:

1. **Droid exec auth gap**: `droid exec` failed before taking any action because the shell environment had no `FACTORY_API_KEY`, producing `402 status code (no body)` / `Exec failed`.
2. **Eval task drift gap**: two capability tasks failed during setup because their injected test patches no longer apply cleanly to the current HackerNews SUT.
3. **Prompt-to-command-surface gap**: the eval prompts force `xc`-only workflows but do not teach the agent the relevant `xc` commands for tests, screenshots, or deeplinks, even though `xc-cli` appears to expose them.

## Raw benchmark outcomes

From `runs/20260405_014518/runs.csv`:

| Task | Result | Failure reason | Notes |
|---|---|---|---|
| `feature_from_task_md_fix_tests` | Fail | `setup_failed` | Agent never started; setup failed before transcript/tool use |
| `smoke_build_install_launch` | Fail | `app_not_installed` | Transcript shows `droid exec` returned `Exec failed` immediately |
| `hn_api_cache_ttl` | Fail | `tests_failed` | Transcript shows `Exec failed`; grader later ran tests and found failure |
| `hn_offline_api_refactor` | Fail | `setup_failed` | Agent never started; setup failed before transcript/tool use |
| `hn_settings_deeplink` | Fail | `screenshot_not_found:settings_screenshot.png` | Transcript shows `Exec failed` immediately |

Summary file: `runs/20260405_014518/summary.md`

## Confirmed root causes

### 1) `droid exec` could not authenticate in harness shells

Direct reproduction:
- `FACTORY_API_KEY` in shell: `unset`
- `droid exec --auto medium --output-format stream-json --model gpt-5.4 "Respond with exactly OK and exit."`
- Result: `402 status code (no body)` then `Exec failed`

Impact:
- Any task that depended on the agent actually running was dead on arrival.
- This explains the smoke/deeplink/task transcripts that contain only `Exec failed`.

Why this matters:
- The harness is currently suitable for Codex/Claude auth isolation, but not for `droid exec` unless Factory auth is injected into the clean agent environment.

### 2) Two eval tasks are stale against the current HackerNews SUT

Reproduction:
- `git apply --check --directory ios task_assets/hn_relative_date/add_failing_tests.patch` fails
- `git apply --check --directory ios task_assets/hn_offline_api_refactor/add_failing_tests.patch` fails

Observed error:
- Patch failed at `ios/HackerNewsTests/Hacker_NewsTests.swift:33`

Impact:
- `feature_from_task_md_fix_tests`
- `hn_offline_api_refactor`

These currently cannot be used as reliable measures of agent or `xc-cli` quality until the task assets are rebased.

### 3) The benchmark prompts under-specify the `xc-cli` command surface

The harness tells the agent:
- use `xc` commands only
- do not use raw `xcodebuild`, `xcrun`, or `simctl`

But for non-smoke tasks it does **not** teach the agent the relevant `xc` alternatives.

Relevant `xc-cli` capabilities present in the repo:
- `xc quality.test` with `--only-testing`
- `xc screenshot`
- `xc ui.open-url`
- `xc dev.run`
- `xc dev.launch`

This means the current eval prompt is effectively testing whether the model can discover the exact `xc` surface unaided under one-shot conditions, not just whether `xc-cli` can solve the task.

## What looks like real product/readiness gaps for xc-cli

These are the gaps most worth improving if the goal is for agents to perform well on this eval style:

### A. Agent discoverability gap

`xc-cli` has the needed commands, but the eval success path depends on fast discovery.

Recommended improvements:
- Make `xc --help` / command-group help much more agent-optimized with direct examples for:
  - run app on simulator
  - run one test class via `quality.test --only-testing`
  - open deeplink via `ui.open-url`
  - capture simulator screenshot via `screenshot`
- Ensure top-level help surfaces these commands near `dev.run`.
- Consider a compact "AI quickstart" help mode or aliases optimized for eval prompts.

### B. Workflow packaging gap

The eval tasks want high-level workflows, but the current successful path may require chaining several commands.

Recommended improvements:
- Add or promote higher-level workflows such as:
  - `xc quality.verify.app`
  - a deeplink + screenshot oriented workflow
  - narrower test-focused examples using `quality.test --only-testing`
- If not already present, consider a single command for “open deeplink and capture screenshot on simulator”.

### C. Skill/prompt packaging gap

The eval suite already copies `skills/xc-cli/SKILL.md`, but the benchmark still failed before that mattered.
Once auth is fixed, the next likely limiter is whether the skill gives explicit recipes for the eval task families.

Recommended improvements:
- Update the xc-cli skill prompt with explicit task recipes:
  - smoke build/install/launch -> `xc dev run --simulator --json`
  - run specific failing tests -> `xc quality test --project ... --scheme ... --only-testing ... --json`
  - deeplink -> `xc ui open-url ...`
  - screenshot -> `xc screenshot ...`
- Include exact examples using `project`, `scheme`, `destination`, and simulator targeting.

## Non-product gaps to fix before trusting future benchmark runs

### Harness fixes

1. Inject Factory auth for `droid exec`
   - export `FACTORY_API_KEY` into the clean agent env, or
   - configure the harness to preserve the needed auth material for Droid.

2. Add a preflight auth check for `droid_exec_cli`
   - run a tiny `droid exec` smoke command before the main suite.
   - fail fast with a clear message if auth is missing.

3. Rebase stale task patches
   - update `hn_relative_date` and `hn_offline_api_refactor` patches against the current HackerNews repo.

4. Add a prompt variant tailored to `xc-cli`
   - if the evaluation goal is product capability rather than command discovery, prime with the exact `xc` verbs required for each task family.

### Factory BYOK/custom model fix

Your local `~/.factory/settings.json` currently defines GPT-5.4 custom models with `provider: "generic-chat-completion-api"`.
For GPT-5+/GPT-4o/o-series/Codex, Factory docs require `provider: "openai"` (Responses API).

This did not block the built-in `gpt-5.4` run above, but it **will** block custom GPT-5.4 BYOK usage and should be fixed separately.

## Recommended next benchmark sequence

1. Fix harness auth for `droid exec`
2. Rebase stale task patches
3. Re-run `shell_primed` with 1-3 trials
4. Then run `shell_unprimed` to measure true command discoverability
5. Only after that, compare against prior strong baselines like `codex` / `claude-sonnet`

## Bottom line

Today’s 0/5 run should **not** be interpreted as “xc-cli cannot do these jobs.”

The highest-confidence conclusions are:
- the current `droid exec` harness setup is not authenticated,
- two tasks are stale and not runnable as authored,
- and `xc-cli` would benefit from more agent-oriented command discoverability and recipe-level prompt packaging for test/deeplink/screenshot workflows.
