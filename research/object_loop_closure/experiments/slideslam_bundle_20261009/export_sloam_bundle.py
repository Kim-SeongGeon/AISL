#!/usr/bin/env python3
"""Export recorded SlideSLAM 7D map snapshots without interpreting labels."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess


DEFAULT_TOPIC = "/robot0/PoseMstPairFromOthers"
CSV_FIELDS = [
    "snapshot_index", "bag_time_sec", "robot_id", "object_index",
    "label_raw", "x_raw", "y_raw", "z_raw", "dim1_raw", "dim2_raw", "dim3_raw",
]


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(source_root):
    if source_root is None:
        return None
    result = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def collect_snapshots(bag_path, topic):
    import rosbag

    snapshots = []
    label_counts = Counter()
    with rosbag.Bag(str(bag_path), "r") as bag:
        for index, (_, msg, stamp) in enumerate(bag.read_messages(topics=[topic])):
            objects = []
            for object_index, item in enumerate(msg.map_of_labelXYZ):
                values = [float(value) for value in item.labelXYZ]
                if len(values) != 7 or not all(math.isfinite(value) for value in values):
                    raise ValueError("invalid 7D value at snapshot %d object %d" % (index, object_index))
                label_counts[values[0]] += 1
                objects.append(values)
            snapshots.append({
                "snapshot_index": index,
                "bag_time_sec": stamp.to_sec(),
                "robot_id": int(msg.robotID),
                "objects_7d": objects,
            })
    if not snapshots:
        raise ValueError("no messages found for topic %s" % topic)
    return snapshots, label_counts


def write_outputs(output_dir, snapshots, label_counts, bag_path, topic, source_root):
    if output_dir.exists():
        raise FileExistsError("output directory already exists: %s" % output_dir)
    output_dir.mkdir(parents=True)

    json_path = output_dir / "snapshots.json"
    csv_path = output_dir / "objects.csv"
    manifest_path = output_dir / "manifest.json"

    with json_path.open("w", encoding="utf-8") as stream:
        json.dump(snapshots, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")

    object_count = 0
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for snapshot in snapshots:
            for object_index, values in enumerate(snapshot["objects_7d"]):
                row = dict(zip(CSV_FIELDS[4:], values))
                row.update({
                    "snapshot_index": snapshot["snapshot_index"],
                    "bag_time_sec": snapshot["bag_time_sec"],
                    "robot_id": snapshot["robot_id"],
                    "object_index": object_index,
                })
                writer.writerow(row)
                object_count += 1

    manifest = {
        "schema": "slide_slam_raw_7d_bundle_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_bag": str(bag_path.resolve()),
        "input_bag_size_bytes": bag_path.stat().st_size,
        "input_bag_sha256": sha256_file(bag_path),
        "topic": topic,
        "source_root": str(source_root.resolve()) if source_root is not None else None,
        "source_git_head": git_head(source_root),
        "snapshot_count": len(snapshots),
        "object_rows": object_count,
        "objects_per_snapshot": [len(item["objects_7d"]) for item in snapshots],
        "raw_label_counts_across_snapshots": {
            str(key): count for key, count in sorted(label_counts.items())
        },
        "bag_time_sec_first": snapshots[0]["bag_time_sec"],
        "bag_time_sec_last": snapshots[-1]["bag_time_sec"],
        "robot_ids": sorted({item["robot_id"] for item in snapshots}),
        "fields_7d": ["label_raw", "x_raw", "y_raw", "z_raw", "dim1_raw", "dim2_raw", "dim3_raw"],
        "coordinate_frame": "unverified",
        "units": "unverified",
        "object_identity": "not_present_in_7d",
        "semantic_class_interpretation": "not_inferred_from_negative_shape_labels",
        "ground_truth": "not_used",
        "random_seed": "not_applicable_read_only_export",
        "transform_direction": "not_applicable_no_alignment_performed",
        "outputs": {
            "snapshots.json": sha256_file(json_path),
            "objects.csv": sha256_file(csv_path),
        },
    }
    with manifest_path.open("w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bag", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()

    bag_path = args.bag.expanduser()
    output_dir = args.output_dir.expanduser()
    if not bag_path.is_file():
        parser.error("input bag not found: %s" % bag_path)
    if output_dir.exists():
        parser.error("output directory already exists: %s" % output_dir)
    snapshots, label_counts = collect_snapshots(bag_path, args.topic)
    manifest = write_outputs(
        output_dir, snapshots, label_counts, bag_path, args.topic, args.source_root,
    )
    print("output_dir:", output_dir)
    print("snapshots:", manifest["snapshot_count"])
    print("object_rows:", manifest["object_rows"])
    print("last_snapshot_objects:", manifest["objects_per_snapshot"][-1])
    print("raw_label_counts_across_snapshots:", manifest["raw_label_counts_across_snapshots"])


if __name__ == "__main__":
    main()
