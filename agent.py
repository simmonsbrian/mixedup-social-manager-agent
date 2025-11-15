import argparse
import os
import sys
import csv
import subprocess
from dotenv import load_dotenv

load_dotenv()

CALENDAR_DEFAULT = "posts/drafts/mixedup_content_calendar_starter.csv"
AI_CALENDAR_DEFAULT = "posts/drafts/mixedup_ai_calendar.csv"


def ensure_calendar(path: str) -> None:
    """Create a tiny sample calendar if the file does not exist."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Date",
                    "Platform",
                    "PostType",
                    "Caption",
                    "Asset",
                    "Hashtags",
                    "Status",
                    "Notes",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Date": "2025-10-28",
                    "Platform": "Instagram",
                    "PostType": "Gig Teaser",
                    "Caption": "Sunday set sneak peek. What song should open the set?",
                    "Asset": "teaser_15s.mp4",
                    "Hashtags": "#MixedUpBand #CherokeeGA #LiveMusic #CoverBand #WoodstockGA",
                    "Status": "Planned",
                    "Notes": "",
                }
            )


def read_first_row(path: str):
    """Read the first row from a calendar CSV, or None if empty."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return row
    return None


def demo(calendar_path: str) -> int:
    """Print a single demo post to the console."""
    ensure_calendar(calendar_path)
    first = read_first_row(calendar_path)
    if not first:
        print("[info] Calendar is empty.")
        return 0

    print("=== MixedUp Social Manager — Demo Post ===")
    print(f"Date:     {first.get('Date', '')}")
    print(f"Platform: {first.get('Platform', '')}")
    print(f"Type:     {first.get('PostType', '')}")
    print(f"Caption:  {first.get('Caption', '')}")
    print(f"Asset:    {first.get('Asset', '')}")
    print(f"Hashtags: {first.get('Hashtags', '')}")
    print("Status:   Draft")
    print("==========================================")
    return 0


def enrich_calendar(
    in_path: str,
    out_path: str,
    mode: str = "auto",
    overwrite: bool = False,
    city: str = "Woodstock",
    venue: str = "MadLife",
) -> int:
    """
    Call scripts/generate_captions.py to enrich the calendar with captions/hashtags.
    This shells out using the same Python executable you're running agent.py with.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(root_dir, "scripts", "generate_captions.py")

    if not os.path.exists(script_path):
        print(f"[error] Could not find script at {script_path}")
        return 1

    cmd = [
        sys.executable,
        script_path,
        "--in",
        in_path,
        "--out",
        out_path,
        "--mode",
        mode,
        "--city",
        city,
        "--venue",
        venue,
    ]
    if overwrite:
        cmd.append("--overwrite")

    print("[info] Running caption generator:")
    print("       " + " ".join(cmd))

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"[error] Caption generation failed with code {e.returncode}")
        return e.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="MixedUp Social Manager")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Print one demo post from the calendar and exit",
    )
    parser.add_argument(
        "--calendar",
        default=CALENDAR_DEFAULT,
        help=f"Path to calendar CSV for --demo (default: {CALENDAR_DEFAULT})",
    )

    # Enrichment flags
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Enrich a calendar CSV with captions/hashtags using generate_captions.py",
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        default=CALENDAR_DEFAULT,
        help=f"Input calendar CSV for --enrich (default: {CALENDAR_DEFAULT})",
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        default=AI_CALENDAR_DEFAULT,
        help=f"Output calendar CSV for --enrich (default: {AI_CALENDAR_DEFAULT})",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "ai", "local"],
        default="auto",
        help="Caption generation mode: auto (default), ai, or local",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing captions/hashtags when using --enrich",
    )
    parser.add_argument(
        "--city",
        default="Woodstock",
        help="Default city context for captions (used by generator)",
    )
    parser.add_argument(
        "--venue",
        default="MadLife",
        help="Default venue context for captions (used by generator)",
    )

    args = parser.parse_args()

    if args.demo:
        return demo(args.calendar)

    if args.enrich:
        return enrich_calendar(
            in_path=args.in_path,
            out_path=args.out_path,
            mode=args.mode,
            overwrite=args.overwrite,
            city=args.city,
            venue=args.venue,
        )

    # If no flags passed, just show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
