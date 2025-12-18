import requests

STUDENT_ID = "22MH1A42I8"
GITHUB_REPO_URL = "https://github.com/saladibhaskar/pki-2fa-microservice"
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

with open("student_public.pem") as f:
    public_key = f.read()

payload = {
    "student_id": STUDENT_ID,
    "github_repo_url": GITHUB_REPO_URL,
    "public_key": public_key
}

response = requests.post(API_URL, json=payload, timeout=30)
response.raise_for_status()

data = response.json()
print(data)

with open("encrypted_seed.txt", "w") as f:
    f.write(data["encrypted_seed"])

print("Encrypted seed saved to encrypted_seed.txt")
