#!/usr/bin/env python3
"""Read-only timestamp/frame audit for SlideSLAM input and bundle bags."""

import argparse
from collections import Counter
import json


def point_and_odom_summary(path):
    import rosbag

    topics = ("/semantic_point_cloud", "/aft_mapped_to_init")
    result = {name: {"count": 0, "frames": Counter()} for name in topics}
    result["/aft_mapped_to_init"]["child_frames"] = Counter()
    paired = []
    pending = {}
    with rosbag.Bag(path, "r") as bag:
        for topic, msg, bag_stamp in bag.read_messages(topics=list(topics)):
            item = result[topic]
            item["count"] += 1
            item["frames"][msg.header.frame_id] += 1
            if topic == "/aft_mapped_to_init":
                item["child_frames"][msg.child_frame_id] += 1
            stamp = msg.header.stamp.to_sec()
            if item["count"] == 1:
                item["first_header_sec"] = stamp
                item["first_bag_sec"] = bag_stamp.to_sec()
            item["last_header_sec"] = stamp
            item["last_bag_sec"] = bag_stamp.to_sec()
            key = (topic, item["count"] - 1)
            pending[key] = stamp
            other = topics[0] if topic == topics[1] else topics[1]
            other_key = (other, item["count"] - 1)
            if other_key in pending:
                paired.append(abs(stamp - pending.pop(other_key)))
                pending.pop(key)
    for item in result.values():
        item["frames"] = dict(item["frames"])
        if "child_frames" in item:
            item["child_frames"] = dict(item["child_frames"])
    result["same_index_header_delta_sec"] = {
        "pairs": len(paired),
        "max_abs": max(paired) if paired else None,
        "median_abs": sorted(paired)[len(paired) // 2] if paired else None,
        "within_0_01_sec": sum(delta <= 0.01 for delta in paired),
    }
    return result


def bundle_summary(path):
    import rosbag

    topic = "/robot0/PoseMstPairFromOthers"
    result = {"topic": topic, "count": 0, "robot_ids": Counter()}
    with rosbag.Bag(path, "r") as bag:
        for _, msg, bag_stamp in bag.read_messages(topics=[topic]):
            result["count"] += 1
            result["robot_ids"][str(msg.robotID)] += 1
            stamp = bag_stamp.to_sec()
            if result["count"] == 1:
                result["first_bag_sec"] = stamp
                result["first_map_objects"] = len(msg.map_of_labelXYZ)
            result["last_bag_sec"] = stamp
            result["last_map_objects"] = len(msg.map_of_labelXYZ)
    result["robot_ids"] = dict(result["robot_ids"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_bag")
    parser.add_argument("bundle_bag")
    args = parser.parse_args()
    source = point_and_odom_summary(args.input_bag)
    bundle = bundle_summary(args.bundle_bag)
    first_input = source["/semantic_point_cloud"].get("first_header_sec")
    last_input = source["/semantic_point_cloud"].get("last_header_sec")
    if first_input is not None and bundle["count"]:
        bundle["first_minus_input_first_header_sec"] = bundle["first_bag_sec"] - first_input
        bundle["last_minus_input_first_header_sec"] = bundle["last_bag_sec"] - first_input
        bundle["last_minus_input_last_header_sec"] = bundle["last_bag_sec"] - last_input
    output = {"input": source, "bundle": bundle}
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
