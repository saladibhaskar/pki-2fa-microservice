# tools_try_encodings.py
"""
Try three different public_key encodings and POST each to the instructor API.
1) multiline: public_key contains real newlines
2) single-escaped: newlines replaced with \n (backslash + n)
3) double-escaped: newlines replaced with \\n (two backslashes then n)
We send each JSON as raw bytes (data=...) so we know exactly what's posted.
"""
import json, requests, sys
from pathlib import Path

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
STUDENT_ID = "22mh1a42i8"
REPO_URL = "https://github.com/saladibhaskar/pki-2fa-microservice"
PUBFILE = Path("student_public.pem")

def read_pem():
    b = PUBFILE.read_bytes()
    if b.startswith(b'\xef\xbb\xbf'):
        b = b[3:]
    return b.decode("utf-8", errors="replace")

def send(json_text, label):
    print("\n=== TRY:", label, "===\n")
    print("JSON length:", len(json_text))
    print("Preview (first 300 chars):")
    print(json_text[:300])
    print("\nSending...")
    try:
        resp = requests.post(API_URL, data=json_text.encode("utf-8"), headers={"Content-Type":"application/json"}, timeout=30)
    except Exception as e:
        print("Request exception:", repr(e))
        return
    print("HTTP status:", resp.status_code)
    print("Response body:", resp.text)
    # If success and contains encrypted_seed, save it
    try:
        d = resp.json()
    except Exception:
        d = None
    if isinstance(d, dict) and d.get("encrypted_seed"):
        Path("encrypted_seed.txt").write_text(d["encrypted_seed"], encoding="ascii")
        print("Saved encrypted_seed.txt (DO NOT COMMIT). First 120 chars:")
        print(d["encrypted_seed"][:120])

def main():
    pem = read_pem()
    # Variant 1: raw multiline
    payload1 = {"student_id": STUDENT_ID, "github_repo_url": REPO_URL, "public_key": pem}
    j1 = json.dumps(payload1, separators=(",", ":"), ensure_ascii=False)

    # Variant 2: single-escaped: replace newline with backslash+n (two chars \ and n)
    pub2 = pem.replace("\r\n", "\n").replace("\n", "\\n")
    payload2 = {"student_id": STUDENT_ID, "github_repo_url": REPO_URL, "public_key": pub2}
    j2 = json.dumps(payload2, separators=(",", ":"), ensure_ascii=False)

    # Variant 3: double-escaped: string contains double backslashes then n (so JSON source has \\n)
    pub3 = pem.replace("\r\n", "\n").replace("\n", "\\\\n")
    payload3 = {"student_id": STUDENT_ID, "github_repo_url": REPO_URL, "public_key": pub3}
    j3 = json.dumps(payload3, separators=(",", ":"), ensure_ascii=False)

    # Send all three
    send(j1, "multiline (real newlines)")
    send(j2, "single-escaped (\\n)")
    send(j3, "double-escaped (\\\\n)")

if __name__ == "__main__":
    main()
