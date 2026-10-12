#!/usr/bin/env python3
"""Read intensity histograms from selected PointCloud2 messages in a ROS bag."""

import sys
import numpy as np
import rosbag


if len(sys.argv) != 3:
    raise SystemExit("usage: inspect_slideslam_intensity.py BAG TOPIC")

targets = {0, 500, 1000}
seen = 0
with rosbag.Bag(sys.argv[1], "r") as bag:
    for index, (_, msg, stamp) in enumerate(bag.read_messages(topics=[sys.argv[2]])):
        seen += 1
        if index not in targets:
            continue
        fields = {field.name: field for field in msg.fields}
        if msg.point_step != 16 or fields["intensity"].offset != 12 or fields["intensity"].datatype != 7:
            raise ValueError("unexpected PointCloud2 layout at index %d" % index)
        floats = np.frombuffer(msg.data, dtype=">f4" if msg.is_bigendian else "<f4")
        intensity = floats.reshape(-1, 4)[:, 3]
        values, counts = np.unique(intensity, return_counts=True)
        order = np.argsort(counts)[::-1]
        top = [(float(values[i]), int(counts[i])) for i in order[:20]]
        print("index:", index, "bag_time_sec:", stamp.to_sec(), "points:", len(intensity),
              "unique_intensities:", len(values), "top:", top)
print("message_count:", seen)
