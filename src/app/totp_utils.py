import base64
import pyotp
import time
def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex string to base32.
    """
    raw = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(raw).decode('utf-8')
    return b32
def generate_totp_code(hex_seed: str):
    """
    Generate current TOTP code (SHA1, 30s period, 6 digits).
    Returns (code, seconds_remaining).
    """
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, interval=30, digits=6)  # SHA1 by default
    code = totp.now()
    # Seconds remaining in the current 30s window
    period = 30
    now = int(time.time())
    remaining = period - (now % period)
    return code, remaining
def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with ±valid_window periods tolerance (default = ±1 window).
    """
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, interval=30, digits=6)
    return totp.verify(code, valid_window=valid_window)
