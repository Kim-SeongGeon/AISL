#!/usr/bin/env python3
"""Check a SlideSLAM raw 7D export against its source bag and manifest."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(output_dir, offline=False):
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    snapshots = json.loads((output_dir / "snapshots.json").read_text(encoding="utf-8"))
    with (output_dir / "objects.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert len(snapshots) == manifest["snapshot_count"]
    assert len(rows) == manifest["object_rows"]
    assert [len(s["objects_7d"]) for s in snapshots] == manifest["objects_per_snapshot"]
    if not offline:
        assert sha256_file(Path(manifest["input_bag"])) == manifest["input_bag_sha256"]
    for name, expected in manifest["outputs"].items():
        assert sha256_file(output_dir / name) == expected, name
    if manifest["source_root"] and not offline:
        head = subprocess.check_output(
            ["git", "-C", manifest["source_root"], "rev-parse", "HEAD"], text=True,
        ).strip()
        assert head == manifest["source_git_head"]

    labels = Counter()
    row_index = 0
    for snapshot_index, snapshot in enumerate(snapshots):
        assert snapshot["snapshot_index"] == snapshot_index
        assert snapshot["robot_id"] in manifest["robot_ids"]
        for object_index, values in enumerate(snapshot["objects_7d"]):
            assert len(values) == 7 and all(math.isfinite(value) for value in values)
            row = rows[row_index]
            assert int(row["snapshot_index"]) == snapshot_index
            assert float(row["bag_time_sec"]) == snapshot["bag_time_sec"]
            assert int(row["robot_id"]) == snapshot["robot_id"]
            assert int(row["object_index"]) == object_index
            assert [float(row[key]) for key in manifest["fields_7d"]] == values
            labels[values[0]] += 1
            row_index += 1
    assert row_index == len(rows)
    assert {str(key): value for key, value in sorted(labels.items())} == manifest["raw_label_counts_across_snapshots"]
    print("verified: snapshots=%d object_rows=%d labels=%s" % (
        len(snapshots), len(rows), sorted(labels.items()),
    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--offline", action="store_true", help="verify a copy without the source bag or Git checkout")
    args = parser.parse_args()
    verify(args.output_dir, offline=args.offline)
