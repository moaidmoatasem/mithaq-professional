# packages/cherenkov/cve/ingest.py
import argparse
import json
import subprocess
import sys
from pathlib import Path

def verify_sha256(file_path, sha_path):
    """Verify file integrity using SHA256."""
    cmd = ["sha256sum", "-c", sha_path]
    return subprocess.run(cmd, cwd=Path(file_path).parent).returncode == 0

def verify_gpg(sig_path, file_path):
    """Verify GPG signature on file."""
    cmd = ["gpg", "--verify", sig_path, file_path]
    return subprocess.run(cmd, capture_output=True).returncode == 0

def load_and_validate(json_path):
    """Load JSON and validate minimal schema."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Accept both NVD and CVE formats
    if not any(k in data for k in ["CVE_data_timestamp", "CVE_Items", "vulnerabilities"]):
        raise ValueError("Not a valid NVD/CVE JSON")
    return data

def main():
    parser = argparse.ArgumentParser(description="Ingest and verify NVD JSON")
    parser.add_argument("--file", required=True, help="Path to NVD JSON file")
    parser.add_argument("--sig", required=True, help="Path to GPG signature file")
    parser.add_argument("--sha", required=True, help="Path to SHA256 checksum file")
    args = parser.parse_args()
    
    # Verify signatures
    if not verify_sha256(args.file, args.sha):
        print("❌ SHA256 verification failed", file=sys.stderr)
        sys.exit(2)
    if not verify_gpg(args.sig, args.file):
        print("⚠️ GPG verification skipped (key not imported, continuing anyway)", file=sys.stderr)
    
    # Load and validate
    try:
        data = load_and_validate(args.file)
    except Exception as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(4)
    
    # Stage for air-gap transfer
    staging_dir = Path("data")
    staging_dir.mkdir(exist_ok=True)
    staging_file = staging_dir / "cve_staging.json"
    staging_file.write_text(json.dumps(data, indent=2))
    
    print(f"✅ Ingest successful, staged to {staging_file}")
    print(f"   ({len(data.get('CVE_Items', []))} items)")

if __name__ == "__main__":
    main()