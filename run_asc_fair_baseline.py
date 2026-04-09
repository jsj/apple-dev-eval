#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", choices=["xc", "asc", "xcodebuildmcp", "all"], default="all")
    ap.add_argument("--task-id", action="append", dest="task_ids")
    args = ap.parse_args()

    tasks = ROOT / "tasks_asc_fair.yaml"
    configs = []
    if args.tool in ("xc", "all"):
        configs.append(ROOT / "config_asc_fair_minimax_xc.yaml")
    if args.tool in ("asc", "all"):
        configs.append(ROOT / "config_asc_fair_minimax_asc.yaml")
    if args.tool in ("xcodebuildmcp", "all"):
        configs.append(ROOT / "config_asc_fair_minimax_xcodebuildmcp.yaml")

    rc = 0
    for config in configs:
        cmd = [sys.executable, str(ROOT / "run_suite.py"), "--config", str(config), "--tasks", str(tasks)]
        if args.task_ids:
            cmd += ["--task-ids", *args.task_ids]
        rc = run(cmd)
        if rc != 0:
            return rc
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
