#!/usr/bin/env bash
set -euo pipefail

# Ensure UTC
export TZ=UTC
ln -sf /usr/share/zoneinfo/UTC /etc/localtime || true

# Make sure /data and /cron exist and are writable
mkdir -p /data /cron
chmod 755 /data /cron

# Start cron (daemon) in background
service cron start || /etc/init.d/cron start || cron &

# Optional: show last cron rules (helpful for debugging)
echo "Installed crontab:"
crontab -l || true

# Start uvicorn (blocking) - binds to 0.0.0.0:8080
exec python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8080