import argparse
import os
import sys
import csv
from dotenv import load_dotenv

CALENDAR_DEFAULT = "posts/drafts/mixedup_content_calendar_starter.csv"

def ensure_calendar(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "Date","Platform","PostType","Caption","Asset","Hashtags","Status","Notes"
            ])
            w.writeheader()
            w.writerow({
                "Date":"2025-10-28",
                "Platform":"Instagram",
                "PostType":"Gig Teaser",
                "Caption":"Sunday set sneak peek. What song should open the set?",
                "Asset":"teaser_15s.mp4",
                "Hashtags":"#MixedUpBand #CherokeeGA #LiveMusic #CoverBand #WoodstockGA",
                "Status":"Planned",
                "Notes":""
            })

def read_first_row(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            return row
    return None

def demo(calendar_path):
    ensure_calendar(calendar_path)
    first = read_first_row(calendar_path)
    if not first:
        print("[info] Calendar is empty.")
        return 0
    print("=== MixedUp Social Manager — Demo Post ===")
    print(f"Date:     {first.get('Date','')}")
    print(f"Platform: {first.get('Platform','')}")
    print(f"Type:     {first.get('PostType','')}")
    print(f"Caption:  {first.get('Caption','')}")
    print(f"Asset:    {first.get('Asset','')}")
    print(f"Hashtags: {first.get('Hashtags','')}")
    print("Status:   Draft")
    print("==========================================")
    return 0

def main():
    load_dotenv()
    p = argparse.ArgumentParser(description="MixedUp Social Manager (No Pandas)")
    p.add_argument("--demo", action="store_true", help="Print one demo post from the calendar")
    p.add_argument("--calendar", default=CALENDAR_DEFAULT, help="Path to calendar CSV")
    args = p.parse_args()
    if args.demo:
        return demo(args.calendar)
    print("Nothing to do. Try --demo")
    return 0

if __name__ == "__main__":
    sys.exit(main())
