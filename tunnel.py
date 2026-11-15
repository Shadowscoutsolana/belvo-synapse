import os
import sys
import re
import socket
import shutil
import platform
import subprocess
import tarfile
import urllib.request
from pathlib import Path

SYSTEM = platform.system().lower()  # 'windows', 'darwin', 'linux'
MACHINE = platform.machine().lower()  # 'arm64', 'x86_64', 'amd64'

ROOT_DIR = Path(__file__).resolve().parent
LOCAL_BIN = ROOT_DIR / ("cloudflared.exe" if SYSTEM == "windows" else "cloudflared")

def _download_progress(block_num: int, block_size: int, total_size: int):
    if total_size > 0:
        percent = min(100, int(block_num * block_size * 100 / total_size))
        downloaded_mb = (block_num * block_size) / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        sys.stdout.write(f"\r[Cloudflare Tunnel] Downloading: {percent}% ({downloaded_mb:.1f} MB / {total_mb:.1f} MB)...")
        sys.stdout.flush()

def check_local_server(port: int = 8000) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False

def get_download_info() -> tuple[str | None, bool]:
    base = "https://github.com/cloudflare/cloudflared/releases/latest/download"
    if SYSTEM == "windows":
        return f"{base}/cloudflared-windows-amd64.exe", False
    elif SYSTEM == "darwin":
        is_arm = "arm" in MACHINE or "aarch" in MACHINE
        arch = "arm64" if is_arm else "amd64"
        return f"{base}/cloudflared-darwin-{arch}.tgz", True
    elif SYSTEM == "linux":
        is_arm = "arm" in MACHINE or "aarch" in MACHINE
        arch = "arm64" if is_arm else "amd64"
        return f"{base}/cloudflared-linux-{arch}", False
    return None, False

def find_or_download_cloudflared() -> str | None:
    # 1. Check local project directory
    if LOCAL_BIN.exists() and LOCAL_BIN.stat().st_size > 5_000_000:
        if SYSTEM != "windows":
            try:
                os.chmod(LOCAL_BIN, 0o755)
            except Exception:
                pass
        return str(LOCAL_BIN)
    
    # 2. Check system PATH
    system_cf = shutil.which("cloudflared") or shutil.which("cloudflared.exe")
    if system_cf:
        return system_cf
    
    # 3. Check standard Homebrew paths on macOS
    if SYSTEM == "darwin":
        for brew_path in ("/opt/homebrew/bin/cloudflared", "/usr/local/bin/cloudflared"):
            if os.path.exists(brew_path):
                return brew_path

    # 4. Attempt automatic download of official binary
    url, is_tar = get_download_info()
    if not url:
        print(f"[Cloudflare Tunnel] Automatic download not supported for {SYSTEM}-{MACHINE}.")
        return None

    print(f"[Cloudflare Tunnel] 'cloudflared' not found. Downloading official {SYSTEM.capitalize()} binary...")
    try:
        if is_tar:
            tar_path = ROOT_DIR / "cloudflared.tgz"
            urllib.request.urlretrieve(url, str(tar_path), reporthook=_download_progress)
            print("\n[Cloudflare Tunnel] Extracting archive...")
            with tarfile.open(str(tar_path), "r:gz") as tar:
                tar.extract("cloudflared", path=str(ROOT_DIR))
            if tar_path.exists():
                tar_path.unlink()
        else:
            urllib.request.urlretrieve(url, str(LOCAL_BIN), reporthook=_download_progress)

        if SYSTEM != "windows" and LOCAL_BIN.exists():
            os.chmod(LOCAL_BIN, 0o755)

        print(f"\n[Cloudflare Tunnel] Successfully downloaded to {LOCAL_BIN}\n")
        return str(LOCAL_BIN)
    except Exception as e:
        print(f"\n[Cloudflare Tunnel] Automatic download failed: {e}")
        if SYSTEM == "darwin":
            print("\n👉 To install Cloudflare Tunnel on macOS using Homebrew, run:")
            print("   brew install cloudflared\n")
        else:
            print("\n👉 To install manually, see:")
            print("   https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/\n")
        return None

def run_tunnel(port: int = 8000, token: str | None = None):
    cf_bin = find_or_download_cloudflared()
    if not cf_bin:
        sys.exit(1)

    if not check_local_server(port):
        print(f"\n⚠️  [Note] No server detected listening on http://127.0.0.1:{port} yet.")
        print(f"👉 Remember to start the server in another terminal window:")
        print(f"   python run.py\n")

    if not token:
        token = os.environ.get("CLOUDFLARE_TUNNEL_TOKEN")

    if token:
        cmd = [cf_bin, "tunnel", "run", "--token", token]
        print(f"[Cloudflare Tunnel] Starting tunnel with persistent token...")
    else:
        cmd = [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{port}"]
        print(f"[Cloudflare Tunnel] Starting Quick Tunnel targeting http://127.0.0.1:{port}...")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace"
        )
    except Exception as e:
        print(f"[Cloudflare Tunnel] Failed to start tunnel process: {e}")
        sys.exit(1)

    url_found = False
    try:
        for line in process.stdout:
            # Match trycloudflare.com temporary public URL
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match and not url_found:
                url_found = True
                public_url = match.group(0)
                banner = (
                    "\n"
                    + "=" * 65 + "\n"
                    + "  🌐 CLOUDFLARE TUNNEL LIVE!\n"
                    + f"  Public HTTPS URL: {public_url}\n"
                    + f"  Admin Portal:     {public_url}/admin/login\n"
                    + "=" * 65 + "\n"
                )
                print(banner)
            print(line, end="")
    except KeyboardInterrupt:
        print("\n[Cloudflare Tunnel] Terminating tunnel...")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("[Cloudflare Tunnel] Tunnel stopped.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Cloudflare Tunnel for Belvo Synapse")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Local port (default: 8000)")
    parser.add_argument("--token", type=str, default=None, help="Cloudflare Tunnel token (optional)")
    args = parser.parse_args()

    run_tunnel(port=args.port, token=args.token)
