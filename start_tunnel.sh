#!/usr/bin/env bash
# Belvo Synapse - Cloudflare Tunnel Launcher for macOS & Linux

PORT=${1:-8000}
TOKEN=${2:-$CLOUDFLARE_TUNNEL_TOKEN}

echo "============================================="
echo "  Starting Belvo Synapse Cloudflare Tunnel   "
echo "============================================="

# Detect virtual environment python
if [ -f "./.venv/bin/python" ]; then
    PYTHON_BIN="./.venv/bin/python"
elif [ -f "./venv/bin/python" ]; then
    PYTHON_BIN="./venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

if [ -n "$TOKEN" ]; then
    "$PYTHON_BIN" tunnel.py --port "$PORT" --token "$TOKEN"
else
    "$PYTHON_BIN" tunnel.py --port "$PORT"
fi
