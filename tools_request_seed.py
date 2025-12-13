#!/usr/bin/env python3
"""
tools_request_seed.py

Usage (from repo root, with your venv activated):
    python tools_request_seed.py --student-id 22mh1a42i8 --repo-url "https://github.com/saladibhaskar/pki-2fa-microservice"

What it does:
- Reads 'student_public.pem' (must exist in repo root)
- Converts the PEM to a single-line string where newline characters are represented as literal \n sequences
  (exact format the instructor API requires)
- POSTs JSON to the instructor API and saves encrypted_seed to 'encrypted_seed.txt' (ASCII) if returned
- Prints clear diagnostics and exits with non-zero code on failure
"""

import argparse
import json
import sys
import requests
from pathlib import Path

API_URL_DEFAULT = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
PUBKEY_FILE = Path("student_public.pem")
OUT_FILE = Path("encrypted_seed.txt")


def prepare_public_key_single_line(pem_text: str) -> str:
    """
    Convert multi-line PEM into single-line string where each newline is replaced with literal backslash+n.
    Example: "-----BEGIN...\nMII...\n-----END..." -> "-----BEGIN...\\nMII...\\n-----END...\\n"
    NOTE: We append a trailing \\n to match examples that include a final newline in the public_key field.
    """
    # Normalize line endings to \n first
    normalized = pem_text.replace("\r\n", "\n").replace("\r", "\n")
    # Ensure it ends with a newline (the assignment example had a trailing newline)
    if not normalized.endswith("\n"):
        normalized = normalized + "\n"
    # Replace real newlines with literal \n (backslash + n)
    single_line = normalized.replace("\n", "\\n")
    return single_line


def request_seed(student_id: str, github_repo_url: str, api_url: str = API_URL_DEFAULT, timeout: int = 30):
    # Preflight checks
    if not PUBKEY_FILE.exists():
        print(f"ERROR: {PUBKEY_FILE} not found in repo root. Generate and commit student_public.pem first.", file=sys.stderr)
        sys.exit(2)

    # Read public key (preserve exact characters)
    raw = PUBKEY_FILE.read_text(encoding="utf-8")
    # Prepare single-line escaped version required by API
    public_key_single = prepare_public_key_single_line(raw)

    # Build the JSON payload exactly as the instructor spec requires
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_single
    }

    # For debugging: show small preview (not the full key)
    preview = public_key_single[:120].replace("\\n", "\\\\n")  # show actual characters
    print("DEBUG: public_key preview (first 120 chars, escaped for terminal):")
    print(preview)
    # Convert payload to JSON string (compact)
    json_text = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    # Send request with correct headers
    headers = {"Content-Type": "application/json"}
    print(f"Sending POST to {api_url} ...")
    try:
        # We send the JSON string as bytes to avoid any library re-encoding surprises
        resp = requests.post(api_url, data=json_text.encode("utf-8"), headers=headers, timeout=timeout)
    except Exception as e:
        print("Network/Requests error while calling instructor API:", repr(e), file=sys.stderr)
        sys.exit(3)

    # Print status and raw response body for debugging
    print("HTTP status:", resp.status_code)
    print("Response body (first 1000 chars):")
    print(resp.text[:1000])

    # Try to parse JSON response
    try:
        data = resp.json()
    except ValueError:
        print("ERROR: Response was not valid JSON. Aborting.", file=sys.stderr)
        sys.exit(4)

    # Check for encrypted_seed
    if resp.ok and isinstance(data, dict) and data.get("encrypted_seed"):
        encrypted_seed = data["encrypted_seed"]
        # Save as ASCII single-line
        OUT_FILE.write_text(encrypted_seed, encoding="ascii")
        print(f"Success: saved encrypted_seed to {OUT_FILE} (DO NOT COMMIT).")
        return 0
    else:
        # Print server-provided error message if available
        if isinstance(data, dict) and data.get("error"):
            print("Server returned error:", data.get("error"), file=sys.stderr)
        else:
            print("Unexpected response payload:", data, file=sys.stderr)
        sys.exit(5)


def main():
    p = argparse.ArgumentParser(description="Request encrypted seed from instructor API")
    p.add_argument("--student-id", required=True)
    p.add_argument("--repo-url", required=True)
    p.add_argument("--api-url", default=API_URL_DEFAULT)
    p.add_argument("--timeout", type=int, default=30)
    args = p.parse_args()

    return request_seed(student_id=args.student_id, github_repo_url=args.repo_url, api_url=args.api_url, timeout=args.timeout)


if __name__ == "__main__":
    sys.exit(main())
