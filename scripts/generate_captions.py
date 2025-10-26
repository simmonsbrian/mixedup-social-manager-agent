import argparse, csv, os
from captions import generate_caption_and_tags

def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r); fields = r.fieldnames
    return rows, fields

def save_rows(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows: w.writerow(row)

def main():
    p = argparse.ArgumentParser(description="Generate captions/hashtags")
    p.add_argument("--in", dest="in_path", required=True)
    p.add_argument("--out", dest="out_path", required=True)
    p.add_argument("--mode", choices=["auto","ai","local"], default="auto")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--city", default="Woodstock")
    p.add_argument("--venue", default="MadLife")
    args = p.parse_args()

    rows, fields = load_rows(args.in_path)
    need = ["Date","Platform","PostType","Caption","Asset","Hashtags","Status","Notes"]
    fields = list(dict.fromkeys((fields or []) + need))

    updated = 0
    for row in rows:
        post_type = (row.get("PostType") or "").strip()
        if not post_type: continue
        existing_caption = (row.get("Caption") or "").strip()
        if existing_caption and not args.overwrite: continue

        ctx = {
            "city": args.city,
            "venue": args.venue,
            "details": row.get("Notes",""),
            "artist": row.get("Artist",""),
            "poll_a": row.get("PollA","Genesis"),
            "poll_b": row.get("PollB","Coldplay")
        }
        caption, tags, source = generate_caption_and_tags(post_type, ctx, mode=args.mode)
        row["Caption"] = caption
        tag_block = " ".join(tags)
        row["Hashtags"] = ((row.get("Hashtags") or "") + " " + tag_block).strip()
        note = (row.get("Notes") or "").strip()
        row["Notes"] = (note + " " if note else "") + f"[{source}]"
        updated += 1

    save_rows(args.out_path, fields, rows)
    print(f"Updated {updated} rows -> {args.out_path}")

if __name__ == "__main__":
    main()
