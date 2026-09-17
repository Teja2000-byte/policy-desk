"""Start both services locally; Ctrl+C stops both."""

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    if not (ROOT / ".env").exists():
        raise SystemExit("Run python scripts/setup.py first.")
    for port in (8000, 8501):
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise SystemExit(
                    f"Port {port} is already in use. Stop the earlier service or use the separate commands in README.md."
                )
    processes = []
    env = {**os.environ, "API_BASE_URL": "http://127.0.0.1:8000"}
    try:
        processes.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "src.api:create_app",
                    "--factory",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=ROOT,
                env=env,
            )
        )
        for _ in range(100):
            if processes[0].poll() is not None:
                raise SystemExit("Backend could not start. Check the error above and your .env.")
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            raise SystemExit("Backend startup timed out.")
        processes.append(
            subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
                cwd=ROOT,
                env=env,
            )
        )
        print(
            "\nPolicy Desk: http://127.0.0.1:8501\nAPI docs: http://127.0.0.1:8000/docs\nCtrl+C stops both services.",
            flush=True,
        )
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    main()
