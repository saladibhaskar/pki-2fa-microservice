from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import os
# Default path to private key (repo root)
PRIVATE_KEY_PATH = os.path.join(os.getcwd(), 'student_private.pem')
def load_private_key(path: str = None, password: bytes = None):
    """
    Load PEM private key from path. Returns a cryptography private key object.
    """
    p = path or PRIVATE_KEY_PATH
    with open(p, 'rb') as f:
        key_data = f.read()
    return load_pem_private_key(key_data, password=password)
def decrypt_seed(encrypted_seed_b64: str, private_key=None) -> str:
    """
    Decrypt base64-encoded ciphertext with RSA/OAEP-SHA256 and return hex seed string.
    Validates that the result is a 64-character lowercase hex string.
    Raises ValueError on invalid input or decryption error.
    """
    if private_key is None:
        private_key = load_private_key()
    try:
        ct = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError("Invalid base64 encrypted_seed") from e
    try:
        plain = private_key.decrypt(
            ct,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError("RSA decryption failed") from e
    try:
        decoded = plain.decode('utf-8').strip()
    except Exception as e:
        raise ValueError("Decrypted seed is not valid UTF-8") from e
    # Validate hex: 64 chars of 0-9a-f (lowercase). Accept uppercase but normalize.
    seed = decoded.lower()
    if len(seed) != 64 or any(c not in '0123456789abcdef' for c in seed):
        raise ValueError("Decrypted seed is not a 64-character hex string")
    return seed
