from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from src.app.crypto import decrypt_seed
from src.app.totp_utils import generate_totp_code, verify_totp_code
app = FastAPI()
DATA_DIR = os.environ.get('DATA_DIR', '/data')
SEED_PATH = Path(DATA_DIR) / 'seed.txt'
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str
class Verify2FARequest(BaseModel):
    code: str
@app.post('/decrypt-seed')
async def post_decrypt_seed(req: DecryptSeedRequest):
    try:
        seed = decrypt_seed(req.encrypted_seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': 'Decryption failed', 'reason': str(e)})
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        # write seed followed by a real newline character
        with open(SEED_PATH, 'w', encoding='utf-8') as f:
            f.write(seed + '\n')
        try:
            os.chmod(SEED_PATH, 0o600)
        except Exception:
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': 'Failed to persist seed', 'reason': str(e)})
    return {'status': 'ok'}
@app.get('/generate-2fa')
async def get_generate_2fa():
    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail={'error': 'Seed not decrypted yet'})
    try:
        seed = SEED_PATH.read_text(encoding='utf-8').strip()
        code, valid_for = generate_totp_code(seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': 'Failed to generate TOTP', 'reason': str(e)})
    return {'code': code, 'valid_for': valid_for}
@app.post('/verify-2fa')
async def post_verify_2fa(req: Verify2FARequest):
    if not req.code:
        raise HTTPException(status_code=400, detail={'error': 'Missing code'})
    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail={'error': 'Seed not decrypted yet'})
    try:
        seed = SEED_PATH.read_text(encoding='utf-8').strip()
        valid = verify_totp_code(seed, req.code, valid_window=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': 'Verification error', 'reason': str(e)})
    return {'valid': bool(valid)}
@app.get('/health')
async def health():
    return {'status': 'ok'}
