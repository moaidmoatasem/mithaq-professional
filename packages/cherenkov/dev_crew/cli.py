import argparse
import asyncio
from pathlib import Path

from cherenkov.dev_crew.session_manager import update_ssot_status
from cherenkov.dev_crew.swarm_orchestrator import AutonomousSprint


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="CHERENKOV Autonomous PMO & Developer CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--focus",
        type=str,
        required=True,
        help="The feature or module to build (e.g. 'SQLite WAL initialization')",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Target relative file path for output (e.g. 'packages/cherenkov/core/storage/database.py')",
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    target_filepath = project_root / args.file

    print("=" * 51)
    print("CHERENKOV PMO SWARM INITIALIZED")
    print(f"Focus : {args.focus}")
    print(f"Target: {target_filepath}")
    print("=" * 51)

    sprint = AutonomousSprint(focus_area=args.focus, target_filepath=str(target_filepath))
    success = await sprint.execute_sprint()

    if success:
        update_ssot_status(args.focus, target_filepath)
        print("\nSprint successfully closed. Ready for next directive.")
    else:
        print("\nSprint failed. Developer could not pass Validation Gate within iteration limits.")


if __name__ == "__main__":
    asyncio.run(main())
