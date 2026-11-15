import uvicorn
import os
import sys
import socket
import subprocess
import argparse

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Belvo Synapse web application")
    parser.add_argument("--tunnel", action="store_true", help="Launch Cloudflare Tunnel alongside the web server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Port to listen on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0 for all devices)")
    args = parser.parse_args()

    port = args.port
    local_ip = get_local_ip()
    tunnel_proc = None

    if args.tunnel:
        tunnel_script = os.path.join(os.path.dirname(__file__), "tunnel.py")
        if os.path.exists(tunnel_script):
            print("\n[Belvo Synapse] Launching Cloudflare Tunnel in background...")
            tunnel_proc = subprocess.Popen([sys.executable, tunnel_script, "--port", str(port)])

    print("\n" + "=" * 60)
    print(" 🚀 BELVO SYNAPSE SERVER READY")
    print(f" • Local (on this PC):   http://127.0.0.1:{port}")
    if local_ip != "127.0.0.1":
        print(f" • Mobile (Same Wi-Fi):  http://{local_ip}:{port}")
    print(f" • Admin Login:          http://127.0.0.1:{port}/admin/login")
    print("=" * 60 + "\n")

    try:
        uvicorn.run("app.main:app", host=args.host, port=port, reload=True)
    finally:
        if tunnel_proc:
            print("\n[Belvo Synapse] Stopping Cloudflare Tunnel...")
            tunnel_proc.terminate()
            try:
                tunnel_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel_proc.kill()
