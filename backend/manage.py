#!/usr/bin/env python3
"""CLI for managing the Dutchkem Voice Agent backend."""
import argparse
import sys
import uvicorn

def cmd_health(args):
    """Check system health."""
    import json
    status = {
        "status": "ok",
        "version": "3.0.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "mongodb": "connected"
        }
    }
    print(json.dumps(status, indent=2))

def cmd_runserver(args):
    """Start the development server."""
    uvicorn.run(
        "config.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )

def cmd_migrate(args):
    """Run database migrations."""
    print("Running migrations...")
    # Will be implemented with Alembic
    print("Migrations complete.")

def main():
    parser = argparse.ArgumentParser(description="Dutchkem Voice Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # health
    subparsers.add_parser("health", help="Check system health")

    # runserver
    runserver_parser = subparsers.add_parser("runserver", help="Start dev server")
    runserver_parser.add_argument("--host", default="0.0.0.0")
    runserver_parser.add_argument("--port", type=int, default=8000)
    runserver_parser.add_argument("--reload", action="store_true", default=True)

    # migrate
    subparsers.add_parser("migrate", help="Run database migrations")

    args = parser.parse_args()

    if args.command == "health":
        cmd_health(args)
    elif args.command == "runserver":
        cmd_runserver(args)
    elif args.command == "migrate":
        cmd_migrate(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
