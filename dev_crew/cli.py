# packages/cherenkov/dev_crew/cli.py
import argparse
import asyncio
from pathlib import Path

from cherenkov.dev_crew.session_manager import update_ssot_status
from cherenkov.dev_crew.swarm_orchestrator import AutonomousSprint


async def main():
    parser = argparse.ArgumentParser(
        description="CHERENKOV Autonomous PMO & Developer CLI",
        formatter_class=argparse.RawTextHelpLabel,
    )

    parser.add_argument(
        "--focus",
        type=str,
        required=True,
        help="The specific feature or module to build (e.g., 'SQLite WAL initialization')",
    )

    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="The target relative file path for the output (e.g., 'packages/cherenkov/core/storage/database.py')",
    )

    args = parser.parse_args()

    # Resolve absolute path based on project root
    project_root = Path(__file__).resolve().parents[3]
    target_filepath = project_root / args.file

    print("===================================================")
    print("🛡️  CHERENKOV PMO SWARM INITIALIZED")
    print(f"🎯  Focus: {args.focus}")
    print(f"📁  Target: {target_filepath}")
    print("===================================================")

    sprint = AutonomousSprint(focus_area=args.focus, target_filepath=str(target_filepath))

    success = await sprint.execute_sprint()

    if success:
        # Step 4: Close the loop by updating the SSOT
        update_ssot_status(args.focus, target_filepath)
        print("\n✅ Sprint successfully closed. Ready for next directive.")
    else:
        print(
            "\n❌ Sprint failed. Developer could not pass Validation Gate within iteration limits."
        )


if __name__ == "__main__":
    asyncio.run(main())
