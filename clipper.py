import argparse
import csv
import os
import subprocess
from dataclasses import dataclass
from typing import List


RAW_ROOT_DEFAULT = "assets/raw"
OUT_ROOT_DEFAULT = "assets/processed"


@dataclass
class ClipDefinition:
	show_id: str
	source_file: str
	output_file: str
	start: str
	duration: int
	aspect: str
	notes: str = ""


def parse_timecode(value: str) -> str:
	"""Normalize a timecode into a form ffmpeg accepts.

	Supports mm:ss or hh:mm:ss; returns the same string if already valid.
	"""
	value = (value or "").strip()
	if not value:
		raise ValueError("Start time is required and cannot be empty")

	parts = value.split(":")
	if len(parts) == 2:
		# mm:ss -> 00:mm:ss
		return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)}"
	if len(parts) == 3:
		h, m, s = parts
		return f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}"
	# Fallback: let ffmpeg try to interpret
	return value


def parse_clip_map(path: str, verbose: bool = False) -> List[ClipDefinition]:
	if not os.path.exists(path):
		raise FileNotFoundError(f"Clip map CSV not found: {path}")

	clips: List[ClipDefinition] = []
	required_columns = [
		"ShowId",
		"SourceFile",
		"OutputFile",
		"Start",
		"Duration",
		"Aspect",
	]

	with open(path, newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		missing = [c for c in required_columns if c not in (reader.fieldnames or [])]
		if missing:
			raise ValueError(
				f"Clip map is missing required columns: {', '.join(missing)}"
			)

		for i, row in enumerate(reader, start=2):  # header is line 1
			try:
				duration_raw = row.get("Duration", "").strip()
				if not duration_raw:
					raise ValueError("Duration is required")
				duration = int(duration_raw)

				aspect = (row.get("Aspect") or "").strip().lower()
				if aspect not in {"original", "vertical", "square"}:
					raise ValueError(
						f"Unsupported Aspect '{row.get('Aspect')}'. Must be one of original, vertical, square."
					)

				start = parse_timecode(row.get("Start", ""))

				clip = ClipDefinition(
					show_id=(row.get("ShowId") or "").strip(),
					source_file=(row.get("SourceFile") or "").strip(),
					output_file=(row.get("OutputFile") or "").strip(),
					start=start,
					duration=duration,
					aspect=aspect,
					notes=(row.get("Notes") or "").strip(),
				)
				clips.append(clip)
			except Exception as e:
				raise ValueError(f"Error in {path} line {i}: {e}") from e

	if verbose:
		print(f"[info] Loaded {len(clips)} clips from {path}")
	return clips


def build_ffmpeg_command(
	clip: ClipDefinition,
	raw_root: str,
	out_root: str,
	overwrite: bool,
) -> list[str]:
	in_path = os.path.join(raw_root, clip.source_file)
	out_path = os.path.join(out_root, clip.output_file)

	vf_filters = None
	if clip.aspect == "vertical":
		# 1080x1920 center crop pipeline
		vf_filters = "scale=1080:-2,crop=1080:1920"
	elif clip.aspect == "square":
		# 1080x1080 center crop pipeline
		vf_filters = "scale=1080:-2,crop=1080:1080"

	cmd: list[str] = [
		"ffmpeg",
		"-ss",
		clip.start,
		"-t",
		str(clip.duration),
		"-i",
		in_path,
	]

	if overwrite:
		cmd.append("-y")

	cmd.extend([
		"-c:v",
		"libx264",
		"-c:a",
		"aac",
	])

	if vf_filters:
		cmd.extend(["-vf", vf_filters])

	# Ensure output directory exists
	os.makedirs(os.path.dirname(out_path), exist_ok=True)
	cmd.append(out_path)

	return cmd


def run_clip(
	clip: ClipDefinition,
	raw_root: str,
	out_root: str,
	dry_run: bool,
	overwrite: bool,
	verbose: bool,
) -> None:
	in_path = os.path.join(raw_root, clip.source_file)
	out_path = os.path.join(out_root, clip.output_file)

	if not os.path.exists(in_path):
		print(
			f"[error] Missing source file for {clip.show_id}: {in_path} (skipping)"
		)
		return

	if os.path.exists(out_path) and not overwrite:
		if verbose:
			print(f"[info] Output exists, skipping (use --overwrite to force): {out_path}")
		return

	cmd = build_ffmpeg_command(clip, raw_root, out_root, overwrite)

	if dry_run:
		print("[dry-run]", " ".join(cmd))
		return

	if verbose:
		extra = f" notes={clip.notes}" if clip.notes else ""
		print(
			f"[info] ffmpeg for {clip.show_id}: {clip.source_file} -> {clip.output_file}{extra}"
		)

	try:
		result = subprocess.run(cmd, check=True)
		if verbose:
			print(
				f"[info] ffmpeg completed with code {result.returncode} for {clip.output_file}"
			)
	except subprocess.CalledProcessError as e:
		print(
			"[error] ffmpeg failed",
			f"show_id={clip.show_id}",
			f"source={clip.source_file}",
			f"output={clip.output_file}",
			f"code={e.returncode}",
		)


def main() -> int:
	parser = argparse.ArgumentParser(description="MixedUp video clipper")
	parser.add_argument(
		"--map",
		dest="map_path",
		required=True,
		help="Path to clip map CSV",
	)
	parser.add_argument(
		"--raw-root",
		default=RAW_ROOT_DEFAULT,
		help=f"Base folder for source files (default: {RAW_ROOT_DEFAULT})",
	)
	parser.add_argument(
		"--out-root",
		default=OUT_ROOT_DEFAULT,
		help=f"Base folder for output files (default: {OUT_ROOT_DEFAULT})",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Print ffmpeg commands without executing",
	)
	parser.add_argument(
		"--overwrite",
		action="store_true",
		help="Overwrite existing output files",
	)
	parser.add_argument(
		"--verbose",
		action="store_true",
		help="Log more information",
	)

	args = parser.parse_args()

	try:
		clips = parse_clip_map(args.map_path, verbose=args.verbose)
	except Exception as e:
		print(f"[error] {e}")
		return 1

	if not clips:
		if args.verbose:
			print("[info] No clips found in map; nothing to do.")
		return 0

	raw_root = args.raw_root
	out_root = args.out_root

	if args.verbose:
		print(f"[info] raw_root={raw_root}")
		print(f"[info] out_root={out_root}")

	for clip in clips:
		run_clip(
			clip=clip,
			raw_root=raw_root,
			out_root=out_root,
			dry_run=args.dry_run,
			overwrite=args.overwrite,
			verbose=args.verbose,
		)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
