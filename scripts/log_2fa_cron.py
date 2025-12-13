#!/usr/bin/env python3
import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from datetime import datetime, timezone
from src.app.totp_utils import generate_totp_code
DATA_PATH = '/data/seed.txt'
LOG_PATH = '/cron/last_code.txt'
def main():
    try:
        if not os.path.exists(DATA_PATH):
            print(f"ERROR: seed file not found at {DATA_PATH}", file=sys.stderr)
            return 1
        seed = open(DATA_PATH, 'r', encoding='utf-8').read().strip()
        code, _ = generate_totp_code(seed)
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        line = f"{now} - 2FA Code: {code}\n"
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(line)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0
if __name__ == '__main__':
    sys.exit(main())
