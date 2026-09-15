#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build/clipper
clang++ -std=c++14 -O2 -Wno-unknown-pragmas -I third_party/eigen -I third_party/clipper/include \
  virtual_map/clipper_driver.cpp third_party/clipper/src/clipper.cpp \
  third_party/clipper/src/utils.cpp third_party/clipper/src/dsd.cpp \
  third_party/clipper/src/sdp.cpp third_party/clipper/src/maxclique.cpp \
  third_party/clipper/src/invariants/euclidean_distance.cpp \
  third_party/clipper/src/invariants/pointnormal_distance.cpp \
  -o build/clipper/clipper_driver
