#!/usr/bin/env python3
"""Print the schema of the first semantic point cloud in a ROS bag."""

from collections import Counter
import sys
import rosbag


if len(sys.argv) != 3:
    raise SystemExit("usage: inspect_slideslam_input.py BAG TOPIC")

with rosbag.Bag(sys.argv[1], "r") as bag:
    first = None
    schemas = Counter()
    frames = Counter()
    for item in bag.read_messages(topics=[sys.argv[2]]):
        if first is None:
            first = item
        _, msg, _ = item
        schemas[tuple((field.name, field.offset, field.datatype, field.count) for field in msg.fields)] += 1
        frames[msg.header.frame_id] += 1
    if first is None:
        raise SystemExit("topic not found or empty: " + sys.argv[2])
    topic, msg, stamp = first
    print("topic:", topic)
    print("message_type:", msg._type)
    print("bag_time_sec:", stamp.to_sec())
    print("frame_id:", msg.header.frame_id)
    print("width:", msg.width, "height:", msg.height, "point_step:", msg.point_step)
    print("fields:", [(field.name, field.offset, field.datatype, field.count) for field in msg.fields])
    print("message_count:", sum(schemas.values()))
    print("schemas:", schemas.most_common())
    print("frames:", frames.most_common())
