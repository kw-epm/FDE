#!/usr/bin/env python3
"""One command to run the whole prototype — backend + React UI.

    python3 run.py          # from prototype/  (run inside WSL)

Starts both:
  backend  -> http://localhost:8000   (uvicorn server:app)
  frontend -> http://localhost:5173   (Vite dev server; proxies /api -> :8000)  <-- open this

First run auto-installs the UI deps. Ctrl-C stops both.
Set ANTHROPIC_API_KEY first for the live agent path (otherwise the offline mock runs).
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI = ROOT / "ui"


def _stop(procs):
    """Kill each child's whole process group so nothing (uvicorn, vite) lingers."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for _, p in procs:
            if p.poll() is None:
                try:
                    os.killpg(os.getpgid(p.pid), sig)
                except (ProcessLookupError, PermissionError):
                    pass
        time.sleep(1.0)
        if all(p.poll() is not None for _, p in procs):
            break


def main():
    if not (UI / "node_modules").exists():
        print("[run] first run — installing UI deps (npm install)…")
        subprocess.run("npm install", cwd=UI, shell=True, check=True)

    procs = [
        ("backend", subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "server:app", "--port", "8000"],
            cwd=ROOT, start_new_session=True)),
        ("frontend", subprocess.Popen(
            "npm run dev", cwd=UI, shell=True, start_new_session=True)),
    ]

    print("\n  ResolveOne is starting…")
    print("    backend   -> http://localhost:8000")
    print("    frontend  -> http://localhost:5173   <-- open this in your browser")
    print("    provider  -> set ANTHROPIC_API_KEY for the live (Haiku/Sonnet) path\n")
    print("  Ctrl-C to stop both.\n")

    try:
        while all(p.poll() is None for _, p in procs):
            time.sleep(0.5)
        dead = [name for name, p in procs if p.poll() is not None]
        print(f"\n[run] {', '.join(dead)} exited — shutting the rest down.")
    except KeyboardInterrupt:
        print("\n[run] stopping…")
    finally:
        _stop(procs)
        print("[run] stopped.")


if __name__ == "__main__":
    main()
