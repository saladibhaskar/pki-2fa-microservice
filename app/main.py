from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
import time
import pyotp

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

DATA_FILE = "/data/seed.txt"

app = FastAPI()

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str


def load_private_key():
    with open("student_private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def hex_seed_to_totp(hex_seed: str) -> pyotp.TOTP:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()
    return pyotp.TOTP(base32_seed)


@app.post("/decrypt-seed")
def decrypt_seed(req: DecryptRequest):
    try:
        private_key = load_private_key()
        encrypted_bytes = base64.b64decode(req.encrypted_seed)

        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode()

        if len(decrypted) != 64:
            raise ValueError("Invalid seed length")

        os.makedirs("/data", exist_ok=True)
        with open(DATA_FILE, "w") as f:
            f.write(decrypted)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(DATA_FILE) as f:
        hex_seed = f.read().strip()

    totp = hex_seed_to_totp(hex_seed)
    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(DATA_FILE) as f:
        hex_seed = f.read().strip()

    totp = hex_seed_to_totp(hex_seed)
    is_valid = totp.verify(req.code, valid_window=1)

    return {"valid": is_valid}
