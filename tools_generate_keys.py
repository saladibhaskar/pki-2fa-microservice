from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
# Generate RSA 4096-bit with exponent 65537
key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
# Private key PEM, unencrypted (the assignment requires committing this to git)
priv_pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
    encryption_algorithm=serialization.NoEncryption()
)
# Public key PEM (SubjectPublicKeyInfo)
pub_pem = key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
with open('student_private.pem','wb') as f:
    f.write(priv_pem)
with open('student_public.pem','wb') as f:
    f.write(pub_pem)
print('Generated student_private.pem and student_public.pem')
