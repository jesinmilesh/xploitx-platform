#!/usr/bin/env python
"""
XploitX Secret Scanner
Scans files in the repository for accidentally committed secrets, API keys, and credentials.
"""
import os
import re
import sys

PATTERNS = [
    (r"(?i)(?:api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{16,})['\"]", "API/Secret Key"),
    (r"(?i)xkeysib-[a-f0-9]{64}-[a-zA-Z0-9]{16}", "Brevo API Key"),
    (r"(?i)AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)ghp_[0-9a-zA-Z]{36}", "GitHub Personal Access Token"),
    (r"(?i)glpat-[0-9a-zA-Z\-_]{20}", "GitLab Personal Access Token"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private Key"),
    (r"(?i)(?:postgres|mysql|mongodb(?:\+srv)?):\/\/[^\s:]+:[^\s@]+@[^\s\/]+", "Database URI with Password"),
]

EXCLUDE_DIRS = {".git", ".data", "node_modules", "vendor", "__pycache__", "venv", ".venv", "tests"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf", ".eot", ".zip", ".tar", ".gz", ".db"}

DUMMY_KEYS = {
    "AKIAIOSFODNN7EXAMPLE",
    "<YOUR_PASSWORD_HERE>",
    "AAAAAAAAAAAAAAAAAAAA",
    "ctfd:ctfd@",
    "ctfd:password@",
    "root:password@",
    "ctfduser:ctfd@",
    "postgres:postgres@",
    "postgres:password@",
}

def scan():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    findings = []
    
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXCLUDE_EXTS or f == ".env.example":
                continue
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, repo_root)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    for line_no, line in enumerate(fh, 1):
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue
                        if any(dummy in line for dummy in DUMMY_KEYS):
                            continue
                        for pattern, desc in PATTERNS:
                            if re.search(pattern, line):
                                findings.append((rel_path, line_no, desc))
            except Exception as e:
                pass
                
    if findings:
        print(f"[!] Found {len(findings)} potential secret(s):")
        for file_path, line, desc in findings:
            print(f"  - {file_path}:{line} -> {desc}")
        return 1
    else:
        print("[+] Secret scan clean. No sensitive credentials found.")
        return 0

if __name__ == "__main__":
    sys.exit(scan())
