import datetime
from pathlib import Path


def get_ssot_context() -> str:
    """Reads CLAUDE.md to establish the Architect's project context."""
    root_dir = Path(__file__).resolve().parents[3]
    ssot_path = root_dir / "CLAUDE.md"

    if not ssot_path.exists():
        raise FileNotFoundError("CRITICAL: SSOT file CLAUDE.md not found. PMO cannot start.")

    with open(ssot_path, "r", encoding="utf-8") as f:
        return f.read()


def update_ssot_status(focus_area: str, target_file: Path) -> None:
    """Appends a completed sprint log entry to CLAUDE.md."""
    root_dir = Path(__file__).resolve().parents[3]
    ssot_path = root_dir / "CLAUDE.md"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n- **[{timestamp}] COMPLETED:** `{focus_area}` -> `{target_file.name}`"

    try:
        with open(ssot_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"SSOT Updated: Recorded completion of {focus_area}")
    except Exception as e:
        print(f"WARNING: Failed to update SSOT. Error: {e}")
