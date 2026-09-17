"""Build a source-only ZIP; omit local credentials, accounts, and runtime files."""

import argparse
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    "README.md",
    "DEVELOPMENT.md",
    "DATA_NOTES.md",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    ".env.example",
    ".gitignore",
    "streamlit_app.py",
    "run.py",
    "sample_test_cases.json",
}
FOLDERS = {"src", "tests", "scripts", "knowledge_base", "data", "docs", "reports", ".streamlit", ".github"}
ALLOWED_SUFFIXES = {".py", ".md", ".txt", ".json", ".csv", ".toml", ".sql", ".yml", ".yaml"}


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in {"__pycache__", ".pytest_cache", ".ruff_cache", "private"} for part in rel.parts):
        return False
    if path.name.startswith(".env") or path.name == "secrets.toml":
        return rel.as_posix() == ".env.example"
    if len(rel.parts) == 1:
        return rel.name in ROOT_FILES
    return rel.parts[0] in FOLDERS and path.suffix in ALLOWED_SUFFIXES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT.parent / "policy-desk-submission.zip")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and included(path))
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path("policy-desk") / path.relative_to(ROOT))
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise SystemExit("Archive verification failed")
    print(f"Packaged {len(files)} source/documentation files: {args.output}")
    print("SHA-256:", hashlib.sha256(args.output.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
