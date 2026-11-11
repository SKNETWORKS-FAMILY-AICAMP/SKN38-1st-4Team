"""Open the local app, starting Streamlit only when needed."""
from pathlib import Path
import socket
import subprocess
import sys
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import webbrowser

URL = "http://localhost:8501"
_http = build_opener(ProxyHandler({}))
APP_DIR = Path(__file__).resolve().parent


def project_python():
    """Prefer the project's .venv so the editor's interpreter choice doesn't matter."""
    for candidate in (APP_DIR / ".venv" / "bin" / "python",
                      APP_DIR / ".venv" / "Scripts" / "python.exe"):
        if candidate.exists():
            return str(candidate)
    return sys.executable


def server_ready():
    try:
        with _http.open(URL + "/_stcore/health", timeout=1) as response:
            return response.status == 200 and response.read(64).strip() == b"ok"
    except (URLError, TimeoutError, OSError):
        return False


def open_site():
    if not webbrowser.open(URL, new=2):
        print(f"Open this address in your browser: {URL}")


def main():
    if server_ready():
        open_site()
        return 0
    try:
        with socket.create_connection(("localhost", 8501), timeout=1):
            print("A server is already listening on port 8501. Opening the site.")
            open_site()
            return 0
    except OSError:
        pass
    print(f"Starting Streamlit: {URL}", flush=True)
    process = subprocess.Popen(
        [project_python(), "-m", "streamlit", "run", "app.py",
         "--server.headless=false", "--server.port=8501",
         "--browser.serverAddress=localhost", "--browser.serverPort=8501"],
        cwd=APP_DIR,
    )
    try:
        return process.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
