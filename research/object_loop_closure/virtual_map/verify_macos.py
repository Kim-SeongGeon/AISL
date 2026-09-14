"""기존 결과 재현 비교와 학습 그래프의 독립적인 작은 수치 예제 검사."""
import csv
import hashlib
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

from consistency_graph import build_graph, pairwise_consistent, score_graph

root = Path(__file__).resolve().parent
original = root/'results'
reproduced = root/'results_recheck_macos'
with (original/'metrics.csv').open(encoding='utf-8-sig') as f:
    old = list(csv.DictReader(f))
with (reproduced/'metrics.csv').open(encoding='utf-8-sig') as f:
    new = list(csv.DictReader(f))
assert len(old) == len(new) == 210
assert all(n == 30 for n in Counter(r['condition'] for r in new).values())
max_differences = {}
for a, b in zip(old, new):
    assert a.keys() == b.keys()
    for key in a:
        if key == 'condition':
            assert a[key] == b[key]
        else:
            diff = abs(float(a[key])-float(b[key]))
            max_differences[key] = max(max_differences.get(key, 0), diff)
            assert math.isclose(float(a[key]), float(b[key]), rel_tol=1e-12, abs_tol=1e-12), (key, a, b)
for condition in Counter(r['condition'] for r in new):
    assert {int(r['seed']) for r in new if r['condition'] == condition} == set(range(42, 72))
for row in new:
    assert float(row['candidate_recall']) == 1
    if float(row['noise_std_m']) == 0:
        assert float(row['oracle_translation_error_m']) < 1e-9
        assert float(row['oracle_yaw_error_deg']) < 1e-9

# Independent 3-4-5 triangle: exactly known transformed correspondence.
a = [{'xy': p, 'class': 'tree'} for p in [(0, 0), (4, 0), (0, 3)]]
b = [{'xy': p, 'class': 'tree'} for p in [(10, 5), (10, 9), (7, 5)]]
proposed = [(0, 0), (1, 1), (2, 2), (0, 1)]
assert build_graph(a, b, proposed, 0) == [(0, 1), (0, 2), (1, 2)]
assert not pairwise_consistent(a, b, (0, 0), (0, 1), 100)
assert not pairwise_consistent(a, b, (0, 0), (1, 0), 100)
c = [{'xy': p} for p in [(0, 0), (4.25, 0)]]
assert pairwise_consistent(a, c, (0, 0), (1, 1), .25)
assert not pairwise_consistent(a, c, (0, 0), (1, 1), .249)
for epsilon in [-1, float('nan'), float('inf')]:
    try:
        pairwise_consistent(a, b, (0, 0), (1, 1), epsilon)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid epsilon accepted')
edges = build_graph(a, b, proposed, 0)
score_graph(proposed, edges, [(0, 0), (1, 1), (2, 2)])
score_graph(proposed, edges, [(0, 1)])
assert edges == [(0, 1), (0, 2), (1, 2)]

graph_dir = root/'results_graph_macos_20260911'
for folder in graph_dir.iterdir():
    if folder.is_dir():
        payload = json.loads((folder/'graph.json').read_text())
        assert len(payload['edges']) == payload['metrics']['edge_count']
        ElementTree.parse(folder/'graph.svg')
for svg in reproduced.glob('*/maps.svg'):
    ElementTree.parse(svg)
report = dict(status='PASS', python=sys.version, platform=platform.platform(),
              executable=sys.executable, rows=210, seeds=[42, 71], numeric_tolerance=1e-12,
              max_absolute_differences=max_differences,
              code_sha256=hashlib.sha256((root/'experiment.py').read_bytes()).hexdigest(),
              baseline_command=[sys.executable, '-B', 'virtual_map/experiment.py', '--seed', '42',
                                '--trials', '30', '--output', 'virtual_map/results_recheck_macos'],
              graph_checks='3-4-5 triangle, shared indices, inclusive threshold, invalid epsilon, scoring does not mutate edges, JSON/SVG parse',
              byte_equal_files=[str(p.relative_to(original)) for p in original.rglob('*')
                                if p.is_file() and (reproduced/p.relative_to(original)).read_bytes() == p.read_bytes()],
              note='Numerical reproducibility, not automatic registration success; SVG layout not visually checked here')
(reproduced/'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
