import os
import base64
import pyotp
from datetime import datetime, timezone

DATA_FILE = "/data/seed.txt"

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError("Seed file not found")

with open(DATA_FILE) as f:
    hex_seed = f.read().strip()

seed_bytes = bytes.fromhex(hex_seed)
base32_seed = base64.b32encode(seed_bytes).decode()
totp = pyotp.TOTP(base32_seed)

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
code = totp.now()

print(f"{timestamp} - 2FA Code: {code}")
