#!/usr/bin/env python3
"""
Healing API Router — exposes self-healing diagnostics via REST endpoints.

Endpoints:
  GET  /healer/run          — Run diagnostics, return report
  POST /healer/run-and-fix  — Run diagnostics + auto-fix, return report
  GET  /healer/health       — Quick health summary (pass/fail count)
"""
from fastapi import APIRouter
from apps.healer.agent import HealingAgent

router = APIRouter(prefix="/healer", tags=["healer"])


@router.get("/run")
async def run_diagnostics():
    agent = HealingAgent()
    report = agent.run_diagnostics()
    return report.to_dict()


@router.post("/run-and-fix")
async def run_and_fix():
    agent = HealingAgent()
    report = agent.run_diagnostics()
    agent.apply_fixes()
    return report.to_dict()


@router.get("/health")
async def healer_health():
    agent = HealingAgent()
    report = agent.run_diagnostics()
    return {
        "status": "healthy" if report.failed_checks == 0 else "degraded",
        "passed": report.passed_checks,
        "failed": report.failed_checks,
        "total": report.total_checks,
        "critical": len(report.critical_issues),
    }
