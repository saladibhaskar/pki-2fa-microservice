#!/usr/bin/env python3
import base64, subprocess, sys, os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend
# Files (relative to repo root)
PRIVATE_KEY_PATH = "student_private.pem"
INSTRUCTOR_PUB_PATH = "instructor_public.pem"
def abort(msg):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(2)
def load_private_key(path):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())
def load_public_key(path):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(data, backend=default_backend())
def get_commit_hash():
    # returns 40-char hex
    p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    if p.returncode != 0:
        abort("git rev-parse failed: " + p.stderr.strip())
    h = p.stdout.strip()
    if len(h) != 40:
        abort("unexpected commit hash: " + h)
    return h
def sign_message(privkey, message_bytes):
    sig = privkey.sign(
        message_bytes,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return sig
def encrypt_with_pubkey(pubkey, data):
    ct = pubkey.encrypt(
        data,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ct
def main():
    for p in (PRIVATE_KEY_PATH, INSTRUCTOR_PUB_PATH):
        if not os.path.exists(p):
            abort(f"required file not found: {p}")
    commit_hash = get_commit_hash()
    print("Commit hash:", commit_hash)
    priv = load_private_key(PRIVATE_KEY_PATH)
    pub = load_public_key(INSTRUCTOR_PUB_PATH)
    # Sign ASCII commit hash (not binary)
    msg_bytes = commit_hash.encode("utf-8")
    signature = sign_message(priv, msg_bytes)
    # Encrypt signature with instructor public key
    encrypted = encrypt_with_pubkey(pub, signature)
    # Base64 single-line
    b64 = base64.b64encode(encrypted).decode("ascii")
    print("Encrypted signature (base64):")
    print(b64)
    # also write to file
    with open("encrypted_commit_signature.b64", "w", encoding="ascii") as f:
        f.write(b64)
if __name__ == "__main__":
    main()
