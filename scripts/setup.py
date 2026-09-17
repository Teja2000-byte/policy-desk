"""Create local configuration without putting secrets in shell history."""

import argparse
import getpass
import os
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--no-key", action="store_true", help="Generate JWT configuration; add Gemini key later."
    )
    modes.add_argument(
        "--set-key",
        action="store_true",
        help="Set the Gemini key in an existing .env, preserving other settings.",
    )
    args = parser.parse_args()
    target = ROOT / ".env"
    if target.exists() and not args.set_key:
        print(".env already exists; leaving it unchanged. Use --set-key to add or update your Gemini key.")
        return
    key = "" if args.no_key else getpass.getpass("Your Gemini API key (hidden; Enter to add later): ").strip()
    if any(char in key for char in "\r\n\"'"):
        raise SystemExit("Unexpected characters in API key.")
    if args.set_key and not key:
        raise SystemExit("No key entered; configuration left unchanged.")
    if target.exists():
        content = target.read_text()
        replacement = f"GEMINI_API_KEY={key}"
        content = (
            re.sub(r"^GEMINI_API_KEY=.*$", lambda _: replacement, content, flags=re.MULTILINE)
            if re.search(r"^GEMINI_API_KEY=", content, re.MULTILINE)
            else content.rstrip() + "\n" + replacement + "\n"
        )
        temp = ROOT / ".env.tmp"
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as file:
            file.write(content)
        temp.replace(target)
        print("Gemini key saved privately. Restart the backend to use it.")
        return
    content = (
        (ROOT / ".env.example")
        .read_text()
        .replace("GEMINI_API_KEY=", f"GEMINI_API_KEY={key}")
        .replace("replace-with-a-random-secret-of-at-least-32-characters", secrets.token_urlsafe(48))
    )
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as file:
        file.write(content)
    print(
        "Created private .env with a random JWT secret. "
        + ("Gemini key saved." if key else "Add GEMINI_API_KEY before generating decisions.")
    )


if __name__ == "__main__":
    main()
