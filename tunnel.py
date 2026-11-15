import os
import sys
import re
import socket
import shutil
import subprocess
import urllib.request
from pathlib import Path

CLOUDFLARED_DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
LOCAL_EXE = Path(__file__).resolve().parent / "cloudflared.exe"

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

def find_or_download_cloudflared() -> str | None:
    # 1. Check project directory
    if LOCAL_EXE.exists() and LOCAL_EXE.stat().st_size > 10_000_000:
        return str(LOCAL_EXE)
    
    # 2. Check system PATH
    system_cf = shutil.which("cloudflared") or shutil.which("cloudflared.exe")
    if system_cf:
        return system_cf
    
    # 3. Attempt automatic download of official cloudflared binary
    print("[Cloudflare Tunnel] 'cloudflared' not found in PATH or project directory.")
    print(f"[Cloudflare Tunnel] Downloading official Windows binary (~55 MB)...")
    try:
        urllib.request.urlretrieve(CLOUDFLARED_DOWNLOAD_URL, str(LOCAL_EXE), reporthook=_download_progress)
        print(f"\n[Cloudflare Tunnel] Successfully downloaded to {LOCAL_EXE}\n")
        return str(LOCAL_EXE)
    except Exception as e:
        print(f"\n[Cloudflare Tunnel] Automatic download failed: {e}")
        print("\nTo install Cloudflare Tunnel manually:")
        print("  1. Windows Package Manager: winget install --id Cloudflare.cloudflared")
        print("  2. Direct Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
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
