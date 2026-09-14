"""학습용 이진 거리 consistency graph. 실제 CLIPPER/최종 매칭이 아님."""
import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from experiment import candidates, make_maps


def pairwise_consistent(map_a, map_b, first, second, epsilon):
    """정답 정보 없이 위치와 대응 인덱스만 검사한다."""
    if not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError('epsilon must be finite and nonnegative')
    i, j = first
    k, l = second
    if i == k or j == l:
        return False
    return abs(math.dist(map_a[i]['xy'], map_a[k]['xy']) -
               math.dist(map_b[j]['xy'], map_b[l]['xy'])) <= epsilon


def build_graph(map_a, map_b, proposed, epsilon):
    return [(u, v) for u, v in combinations(range(len(proposed)), 2)
            if pairwise_consistent(map_a, map_b, proposed[u], proposed[v], epsilon)]


def score_graph(proposed, edges, ground_truth):
    """이미 생성된 그래프를 사후 채점한다. 결과를 그래프 생성에 되돌리지 않는다."""
    truth = set(map(tuple, ground_truth))
    correct = [tuple(pair) in truth for pair in proposed]
    counts = {0: 0, 1: 0, 2: 0}
    for u, v in edges:
        counts[int(correct[u]) + int(correct[v])] += 1
    return correct, dict(candidate_count=len(proposed), correct_candidates=sum(correct),
                        edge_count=len(edges), true_true_edges=counts[2],
                        true_true_possible=math.comb(len(truth), 2),
                        true_false_edges=counts[1], false_false_edges=counts[0])


def draw_graph(path, proposed, edges, correct, title):
    # Fixed circular node order for epsilon comparisons; truth affects color only.
    n = len(proposed)
    points = [(380 + 285*math.cos(2*math.pi*k/n - math.pi/2),
               365 + 285*math.sin(2*math.pi*k/n - math.pi/2)) for k in range(n)]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="740" viewBox="0 0 760 740">',
           '<rect width="760" height="740" fill="white"/>',
           f'<text x="24" y="28" font-family="sans-serif" font-size="19">{title}</text>',
           '<text x="24" y="52" font-family="sans-serif" font-size="13">Learning graph only; no correspondence selection / no CLIPPER</text>']
    for u, v in edges:
        x1, y1 = points[u]
        x2, y2 = points[v]
        color = '#16a34a' if correct[u] and correct[v] else '#cbd5e1'
        svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-opacity="0.55"/>')
    for k, ((x, y), (i, j)) in enumerate(zip(points, proposed)):
        color = '#15803d' if correct[k] else '#64748b'
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="9" fill="{color}"><title>node {k}: A{i} - B{j}</title></circle>')
        dx, dy = (x-380)/285, (y-365)/285
        svg.append(f'<text x="{x+17*dx:.2f}" y="{y+17*dy+4:.2f}" text-anchor="middle" font-family="sans-serif" font-size="10">{k}</text>')
    svg.append('<text x="24" y="706" font-family="sans-serif" font-size="13">Green: correct hypothesis | Gray: incorrect | IDs: candidate indices in graph.json</text></svg>')
    path.write_text('\n'.join(svg), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Refuse reuse so prior results are preserved.
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, extras, sigma in [('clean', 0, 0), ('extra_5', 5, 0), ('noise_020', 0, .20)]:
        a, b, gt, transform = make_maps(args.seed, extras, sigma)
        proposed = candidates(a, b)
        previous = set()
        for epsilon in (.05, .20, .50):
            edges = build_graph(a, b, proposed, epsilon)
            correct, metrics = score_graph(proposed, edges, gt)
            assert previous <= set(edges), 'epsilon monotonicity'
            assert len(edges) == len(set(edges)), 'duplicate edge'
            assert all(u < v and proposed[u][0] != proposed[v][0] and
                       proposed[u][1] != proposed[v][1] for u, v in edges)
            assert metrics['true_true_possible'] == 45
            if sigma == 0:
                assert metrics['true_true_edges'] == 45, 'clean true edges'
            previous = set(edges)
            row = dict(condition=name, seed=args.seed, extra_objects=extras,
                       noise_std_m=sigma, epsilon_m=epsilon, **metrics)
            rows.append(row)
            folder = args.output / f'{name}_eps_{epsilon:.2f}'
            folder.mkdir()
            payload = dict(map_a=a, map_b=b, candidates=proposed, edges=edges,
                           evaluation_only=dict(ground_truth_pairs=gt, correct_nodes=correct),
                           ground_truth_transform=dict(direction='A_to_B', yaw_rad=transform[0],
                                                       tx_m=transform[1], ty_m=transform[2]), metrics=row)
            (folder/'graph.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
            draw_graph(folder/'graph.svg', proposed, edges, correct, f'{name} | epsilon={epsilon:.2f} m | seed={args.seed}')
            print(f"{name:10} eps={epsilon:.2f}: TT={metrics['true_true_edges']}/45 TF={metrics['true_false_edges']} FF={metrics['false_false_edges']}")
    with (args.output/'metrics.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), python=sys.version,
                    executable=sys.executable, platform=platform.platform(), architecture=platform.machine(),
                    argv=sys.argv, cwd=str(Path.cwd()), seed=args.seed, trials_per_case=1,
                    units='m; internal angles rad', direction='A_to_B',
                    source='Notion 26.09.11 consistency graph learning plan',
                    source_url='https://app.notion.com/p/388c388e8d7181259571f054730a8512',
                    git_commit=None, code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [Path(__file__), Path(__file__).with_name('experiment.py')]},
                    checks=['epsilon monotonicity', 'unique edges', 'no self edges or shared objects',
                            '45 true-true edges for noise-free cases'],
                    limitations='Single seed; educational binary graph, not CLIPPER; no selection or pose estimation')
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('PASS: 9 learning graphs and invariants; no final matching evaluated.')


if __name__ == '__main__':
    main()
