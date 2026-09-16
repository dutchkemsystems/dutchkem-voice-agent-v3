#!/usr/bin/env python3
"""
Healing Workflow — runs diagnostics, auto-fixes, and reports.
Can be run as a cron job, CI step, or on-demand.

Usage:
    python apps/healer/workflow.py
    python apps/healer/workflow.py --json
    python apps/healer/workflow.py --ci    # CI mode: exit 1 on failure
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
from apps.healer.agent import HealingAgent


def run(ci_mode=False, json_output=False):
    agent = HealingAgent()
    report = agent.run_diagnostics()

    if report.failed_checks > 0:
        agent.apply_fixes()

    report_after_fix = agent.run_diagnostics()

    if json_output:
        print(json.dumps(report_after_fix.to_dict(), indent=2))
    else:
        agent.print_report(report_after_fix)

    if ci_mode and report_after_fix.failed_checks > 0:
        sys.exit(1)

    agent.save_report()
    return report_after_fix


if __name__ == "__main__":
    ci = "--ci" in sys.argv
    js = "--json" in sys.argv
    run(ci_mode=ci, json_output=js)
