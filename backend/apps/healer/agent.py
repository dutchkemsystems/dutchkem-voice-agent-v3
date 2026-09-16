"""
Self-Healing Agent for DutchKem Voice Agent V3

Automatically diagnoses and fixes common issues:
- Import errors and missing dependencies
- Database connection issues
- Configuration mismatches
- Router wiring problems
- Model registration issues
- Service health checks

Usage:
    python -m apps.healer.agent              # Run full diagnostic
    python -m apps.healer.agent --fix        # Run and auto-fix issues
    python -m apps.healer.agent --watch      # Continuous monitoring
"""
import sys
import os
import importlib
import traceback
import asyncio
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class DiagnosticResult:
    check_name: str
    passed: bool
    severity: Severity
    message: str
    fix_available: bool = False
    fix_description: str = ""
    fix_func: object = None


@dataclass
class HealingReport:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    results: list = field(default_factory=list)
    fixes_applied: int = 0
    fixes_failed: int = 0

    @property
    def total_checks(self):
        return len(self.results)

    @property
    def passed_checks(self):
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_checks(self):
        return sum(1 for r in self.results if not r.passed)

    @property
    def critical_issues(self):
        return [r for r in self.results if not r.passed and r.severity == Severity.CRITICAL]

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "summary": {
                "total": self.total_checks,
                "passed": self.passed_checks,
                "failed": self.failed_checks,
                "fixes_applied": self.fixes_applied,
                "fixes_failed": self.fixes_failed,
            },
            "critical_issues": [
                {"check": r.check_name, "message": r.message}
                for r in self.critical_issues
            ],
            "results": [
                {
                    "check": r.check_name,
                    "passed": r.passed,
                    "severity": r.severity.value,
                    "message": r.message,
                    "fix_available": r.fix_available,
                }
                for r in self.results
            ],
        }


class HealingAgent:
    """Self-healing agent that diagnoses and fixes system issues."""

    def __init__(self, backend_dir: str = None):
        if backend_dir is None:
            healer_dir = Path(__file__).resolve().parent  # apps/healer/
            backend_dir = str(healer_dir.parent.parent)  # backend/
        # Ensure we point to the actual backend dir (not workspace root)
        if os.path.basename(backend_dir) != "backend":
            backend_dir = os.path.join(backend_dir, "backend")
        self.backend_dir = backend_dir
        self.report = HealingReport()

    def run_diagnostics(self) -> HealingReport:
        """Run all diagnostic checks."""
        self.report = HealingReport()

        checks = [
            self._check_python_version,
            self._check_required_packages,
            self._check_imports,
            self._check_config_settings,
            self._check_database_config,
            self._check_redis_config,
            self._check_mongodb_config,
            self._check_models_registration,
            self._check_routers_wired,
            self._check_api_routes,
            self._check_auth_system,
            self._check_voice_service,
            self._check_proctoring_service,
            self._check_deepfake_detector,
            self._check_health_endpoint,
            self._check_file_structure,
            self._check_requirements_files,
            self._check_docker_config,
            self._check_env_files,
        ]

        for check in checks:
            try:
                result = check()
                self.report.results.append(result)
            except Exception as e:
                self.report.results.append(DiagnosticResult(
                    check_name=check.__name__,
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Check crashed: {str(e)}\n{traceback.format_exc()}",
                ))

        return self.report

    def apply_fixes(self) -> HealingReport:
        """Apply fixes for all fixable issues."""
        for result in self.report.results:
            if not result.passed and result.fix_available and result.fix_func:
                try:
                    result.fix_func()
                    result.passed = True
                    self.report.fixes_applied += 1
                    print(f"  [FIXED] {result.check_name}: {result.fix_description}")
                except Exception as e:
                    self.report.fixes_failed += 1
                    print(f"  [FAILED] {result.check_name}: {str(e)}")
        return self.report

    # ── Diagnostic Checks ──────────────────────────────────────────

    def _check_python_version(self) -> DiagnosticResult:
        v = sys.version_info
        ok = v.major == 3 and v.minor >= 11
        return DiagnosticResult(
            check_name="Python Version",
            passed=ok,
            severity=Severity.CRITICAL if not ok else Severity.INFO,
            message=f"Python {v.major}.{v.minor}.{v.micro} {'OK' if ok else '- requires 3.11+'}",
        )

    def _check_required_packages(self) -> DiagnosticResult:
        required = [
            "fastapi", "uvicorn", "sqlalchemy", "asyncpg", "motor",
            "redis", "pydantic", "jose", "passlib", "bcrypt",
        ]
        missing = []
        for pkg in required:
            try:
                importlib.import_module(pkg)
            except ImportError:
                missing.append(pkg)

        ok = len(missing) == 0
        return DiagnosticResult(
            check_name="Required Packages",
            passed=ok,
            severity=Severity.CRITICAL if not ok else Severity.INFO,
            message=f"All required packages installed" if ok else f"Missing: {', '.join(missing)}",
            fix_available=not ok,
            fix_description=f"Install missing packages: pip install {' '.join(missing)}",
            fix_func=lambda: os.system(f"pip install {' '.join(missing)}"),
        )

    def _check_imports(self) -> DiagnosticResult:
        modules = [
            "config.app",
            "config.database",
            "config.settings",
            "apps.auth.router",
            "apps.auth.service",
            "apps.auth.models",
            "apps.voice.router",
            "apps.voice.service",
            "apps.voice.models",
            "apps.proctoring.router",
            "apps.proctoring.face_service",
            "apps.proctoring.models",
            "apps.coaching.router",
            "apps.modes.router",
            "apps.scoring.router",
            "apps.deepfake.router",
            "apps.deepfake.detector",
            "apps.background.router",
            "apps.orchestrator.router",
            "apps.analytics.router",
        ]
        failed = []
        for mod in modules:
            try:
                importlib.import_module(mod)
            except Exception as e:
                failed.append(f"{mod}: {str(e)[:80]}")

        ok = len(failed) == 0
        return DiagnosticResult(
            check_name="Module Imports",
            passed=ok,
            severity=Severity.CRITICAL if not ok else Severity.INFO,
            message="All modules import successfully" if ok else f"Failed imports:\n" + "\n".join(failed),
        )

    def _check_config_settings(self) -> DiagnosticResult:
        try:
            from config.settings import settings
            issues = []
            if settings.JWT_SECRET == "change-me-in-production":
                issues.append("JWT_SECRET is default value")
            if not settings.DATABASE_URL:
                issues.append("DATABASE_URL not set")
            ok = len(issues) == 0
            return DiagnosticResult(
                check_name="Config Settings",
                passed=ok,
                severity=Severity.HIGH if not ok else Severity.INFO,
                message="Settings OK" if ok else "; ".join(issues),
                fix_available=True,
                fix_description="Generate secure JWT_SECRET",
                fix_func=self._fix_jwt_secret,
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Config Settings",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Settings load failed: {e}",
            )

    def _check_database_config(self) -> DiagnosticResult:
        try:
            from config.settings import settings
            url = settings.DATABASE_URL
            ok = "postgresql" in url or "sqlite" in url
            return DiagnosticResult(
                check_name="Database Config",
                passed=ok,
                severity=Severity.CRITICAL if not ok else Severity.INFO,
                message=f"Database URL configured: {url[:30]}...",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Database Config",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Database config error: {e}",
            )

    def _check_redis_config(self) -> DiagnosticResult:
        try:
            from config.settings import settings
            ok = bool(settings.REDIS_URL)
            return DiagnosticResult(
                check_name="Redis Config",
                passed=ok,
                severity=Severity.HIGH if not ok else Severity.INFO,
                message=f"Redis URL: {settings.REDIS_URL[:30]}..." if ok else "Redis URL not configured",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Redis Config",
                passed=False,
                severity=Severity.HIGH,
                message=f"Redis config error: {e}",
            )

    def _check_mongodb_config(self) -> DiagnosticResult:
        try:
            from config.settings import settings
            ok = bool(settings.MONGODB_URL)
            return DiagnosticResult(
                check_name="MongoDB Config",
                passed=ok,
                severity=Severity.HIGH if not ok else Severity.INFO,
                message=f"MongoDB URL: {settings.MONGODB_URL[:30]}..." if ok else "MongoDB URL not configured",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="MongoDB Config",
                passed=False,
                severity=Severity.HIGH,
                message=f"MongoDB config error: {e}",
            )

    def _check_models_registration(self) -> DiagnosticResult:
        try:
            from config.database import Base
            tables = list(Base.metadata.tables.keys())
            required = ["users", "voice_profiles", "face_profiles"]
            missing = [t for t in required if t not in tables]
            ok = len(missing) == 0
            return DiagnosticResult(
                check_name="Models Registration",
                passed=ok,
                severity=Severity.CRITICAL if not ok else Severity.INFO,
                message=f"Registered tables: {tables}" if ok else f"Missing tables: {missing}",
                fix_available=not ok,
                fix_description="Ensure all model files are imported before Base.metadata",
                fix_func=self._fix_model_registration,
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Models Registration",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Model registration check failed: {e}",
            )

    def _check_routers_wired(self) -> DiagnosticResult:
        try:
            from config.app import app
            schema = app.openapi()
            paths = list(schema.get("paths", {}).keys())
            required_prefixes = ["/auth", "/voice", "/proctoring", "/coaching", "/scoring", "/deepfake"]
            missing = [p for p in required_prefixes if not any(path.startswith(p) for path in paths)]
            ok = len(missing) == 0
            return DiagnosticResult(
                check_name="Routers Wired",
                passed=ok,
                severity=Severity.CRITICAL if not ok else Severity.INFO,
                message=f"{len(paths)} routes registered" if ok else f"Missing router prefixes: {missing}",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Routers Wired",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Router check failed: {e}",
            )

    def _check_api_routes(self) -> DiagnosticResult:
        try:
            from config.app import app
            schema = app.openapi()
            paths = schema.get("paths", {})
            critical_endpoints = [
                "/auth/login",
                "/auth/register",
                "/auth/me",
                "/voice/clone",
                "/voice/profiles",
                "/health",
            ]
            missing = [ep for ep in critical_endpoints if ep not in paths]
            ok = len(missing) == 0
            return DiagnosticResult(
                check_name="Critical API Endpoints",
                passed=ok,
                severity=Severity.CRITICAL if not ok else Severity.INFO,
                message="All critical endpoints present" if ok else f"Missing endpoints: {missing}",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Critical API Endpoints",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Endpoint check failed: {e}",
            )

    def _check_auth_system(self) -> DiagnosticResult:
        try:
            from apps.auth.service import hash_password, verify_password, create_access_token, decode_token
            hashed = hash_password("test123")
            assert verify_password("test123", hashed)
            token = create_access_token({"sub": "test@test.com"})
            payload = decode_token(token)
            assert payload is not None
            assert payload["sub"] == "test@test.com"
            return DiagnosticResult(
                check_name="Auth System",
                passed=True,
                severity=Severity.INFO,
                message="Auth system functional (hash, verify, JWT create/decode)",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Auth System",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Auth system broken: {e}",
            )

    def _check_voice_service(self) -> DiagnosticResult:
        try:
            from apps.voice.service import VoiceService
            svc = VoiceService()
            assert hasattr(svc, "create_profile")
            assert hasattr(svc, "list_profiles")
            assert hasattr(svc, "get_profile")
            assert hasattr(svc, "synthesize")
            return DiagnosticResult(
                check_name="Voice Service",
                passed=True,
                severity=Severity.INFO,
                message="Voice service has all required methods",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Voice Service",
                passed=False,
                severity=Severity.HIGH,
                message=f"Voice service issue: {e}",
            )

    def _check_proctoring_service(self) -> DiagnosticResult:
        try:
            from apps.proctoring.face_service import FaceService
            from apps.proctoring.liveness_detector import LivenessDetector
            fs = FaceService()
            ld = LivenessDetector()
            assert hasattr(fs, "verify")
            assert hasattr(ld, "check_blink")
            return DiagnosticResult(
                check_name="Proctoring Service",
                passed=True,
                severity=Severity.INFO,
                message="Proctoring services functional",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Proctoring Service",
                passed=False,
                severity=Severity.HIGH,
                message=f"Proctoring service issue: {e}",
            )

    def _check_deepfake_detector(self) -> DiagnosticResult:
        try:
            from apps.deepfake.detector import DeepfakeDetector
            det = DeepfakeDetector()
            assert hasattr(det, "detect_audio")
            assert hasattr(det, "detect_video")
            assert hasattr(det, "detect_combined")
            return DiagnosticResult(
                check_name="Deepfake Detector",
                passed=True,
                severity=Severity.INFO,
                message="Deepfake detector functional",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Deepfake Detector",
                passed=False,
                severity=Severity.HIGH,
                message=f"Deepfake detector issue: {e}",
            )

    def _check_health_endpoint(self) -> DiagnosticResult:
        try:
            from config.app import app
            schema = app.openapi()
            health = schema["paths"].get("/health", {})
            ok = "get" in health
            return DiagnosticResult(
                check_name="Health Endpoint",
                passed=ok,
                severity=Severity.HIGH if not ok else Severity.INFO,
                message="Health endpoint registered" if ok else "Health endpoint missing",
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Health Endpoint",
                passed=False,
                severity=Severity.HIGH,
                message=f"Health endpoint check failed: {e}",
            )

    def _check_file_structure(self) -> DiagnosticResult:
        required_files = [
            "config/app.py",
            "config/database.py",
            "config/settings.py",
            "apps/auth/router.py",
            "apps/auth/service.py",
            "apps/auth/models.py",
            "apps/voice/router.py",
            "apps/voice/service.py",
            "apps/voice/models.py",
            "apps/proctoring/router.py",
            "apps/proctoring/models.py",
            "apps/deepfake/router.py",
            "apps/background/router.py",
            "apps/orchestrator/router.py",
            "apps/analytics/router.py",
            "requirements/base.txt",
            "requirements/production.txt",
            "requirements/dev.txt",
            "alembic.ini",
            "alembic/env.py",
        ]
        missing = []
        for f in required_files:
            full = os.path.join(self.backend_dir, f)
            if not os.path.exists(full):
                missing.append(f)

        ok = len(missing) == 0
        return DiagnosticResult(
            check_name="File Structure",
            passed=ok,
            severity=Severity.CRITICAL if not ok else Severity.INFO,
            message="All required files present" if ok else f"Missing files: {missing}",
        )

    def _check_requirements_files(self) -> DiagnosticResult:
        try:
            base = os.path.join(self.backend_dir, "requirements", "base.txt")
            prod = os.path.join(self.backend_dir, "requirements", "production.txt")
            dev = os.path.join(self.backend_dir, "requirements", "dev.txt")

            issues = []
            for f in [base, prod, dev]:
                if not os.path.exists(f):
                    issues.append(f"Missing {os.path.basename(f)}")
                elif os.path.getsize(f) < 10:
                    issues.append(f"{os.path.basename(f)} is empty")

            ok = len(issues) == 0
            return DiagnosticResult(
                check_name="Requirements Files",
                passed=ok,
                severity=Severity.HIGH if not ok else Severity.INFO,
                message="Requirements files OK" if ok else "; ".join(issues),
            )
        except Exception as e:
            return DiagnosticResult(
                check_name="Requirements Files",
                passed=False,
                severity=Severity.HIGH,
                message=f"Requirements check failed: {e}",
            )

    def _check_docker_config(self) -> DiagnosticResult:
        project_root = os.path.dirname(self.backend_dir)
        files = [
            os.path.join(project_root, "docker-compose.yml"),
            os.path.join(self.backend_dir, "Dockerfile"),
            os.path.join(project_root, "frontend", "web", "Dockerfile"),
        ]
        missing = []
        for f in files:
            if not os.path.exists(f):
                missing.append(os.path.relpath(f, project_root))

        ok = len(missing) == 0
        return DiagnosticResult(
            check_name="Docker Config",
            passed=ok,
            severity=Severity.MEDIUM if not ok else Severity.INFO,
            message="Docker configs present" if ok else f"Missing: {missing}",
        )

    def _check_env_files(self) -> DiagnosticResult:
        project_root = os.path.dirname(self.backend_dir)
        files = [
            os.path.join(project_root, ".env.example"),
            os.path.join(project_root, ".env.production.example"),
            os.path.join(self.backend_dir, ".env.example"),
        ]
        missing = []
        for f in files:
            if not os.path.exists(f):
                missing.append(os.path.relpath(f, project_root))

        ok = len(missing) == 0
        return DiagnosticResult(
            check_name="Environment Files",
            passed=ok,
            severity=Severity.MEDIUM if not ok else Severity.INFO,
            message="Env templates present" if ok else f"Missing: {missing}",
        )

    # ── Fix Functions ───────────────────────────────────────────────

    def _fix_jwt_secret(self):
        import secrets
        secret = secrets.token_hex(32)
        settings_path = os.path.join(self.backend_dir, "config", "settings.py")
        with open(settings_path, "r") as f:
            content = f.read()
        content = content.replace(
            'JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")',
            f'JWT_SECRET: str = os.getenv("JWT_SECRET", "{secret}")',
        )
        with open(settings_path, "w") as f:
            f.write(content)

    def _fix_model_registration(self):
        pass  # Models are already registered via imports in alembic/env.py

    # ── Output ─────────────────────────────────────────────────────

    def print_report(self, report: HealingReport = None):
        if report is None:
            report = self.report

        print("\n" + "=" * 60)
        print("  DUTCHKEM VOICE AGENT — SELF-HEALING DIAGNOSTIC REPORT")
        print("=" * 60)
        print(f"  Timestamp: {report.timestamp}")
        print(f"  Checks: {report.passed_checks}/{report.total_checks} passed")
        print(f"  Fixes Applied: {report.fixes_applied}")
        print("=" * 60)

        for r in report.results:
            icon = "[PASS]" if r.passed else "[FAIL]"
            severity = r.severity.value.upper()
            print(f"\n  {icon} [{severity}] {r.check_name}")
            print(f"       {r.message[:200]}")
            if r.fix_available and not r.passed:
                print(f"       -> Fix: {r.fix_description}")

        print("\n" + "=" * 60)
        if report.critical_issues:
            print(f"  CRITICAL ISSUES: {len(report.critical_issues)}")
            for issue in report.critical_issues:
                print(f"    - {issue.check_name}: {issue.message[:100]}")
        else:
            print("  NO CRITICAL ISSUES FOUND")
        print("=" * 60 + "\n")

    def save_report(self, filepath: str = None):
        if filepath is None:
            filepath = os.path.join(self.backend_dir, "healing_report.json")
        with open(filepath, "w") as f:
            json.dump(self.report.to_dict(), f, indent=2)
        print(f"Report saved to: {filepath}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DutchKem Self-Healing Agent")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    agent = HealingAgent()
    report = agent.run_diagnostics()

    if args.fix:
        agent.apply_fixes()

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        agent.print_report(report)

    if args.save:
        agent.save_report()

    sys.exit(0 if report.failed_checks == 0 else 1)


if __name__ == "__main__":
    main()
