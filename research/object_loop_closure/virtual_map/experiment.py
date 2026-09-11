"""가상 object map 실험. Python 표준 라이브러리만 필요합니다.

매칭은 class all-to-all 기준 방법입니다. SlideGraph/CLIPPER 구현이 아닙니다.
변환 복원은 정답 대응을 이용하는 oracle 점검이며 실제 매칭 성능이 아닙니다.
"""
import argparse
import csv
import json
import math
import random
from pathlib import Path


def transform(point, yaw, tx, ty):
    x, y = point
    c, s = math.cos(yaw), math.sin(yaw)
    return (c*x - s*y + tx, s*x + c*y + ty)


def estimate_transform(source, target):
    """알려진 대응쌍의 2D least-squares 회전 및 이동 복원."""
    if len(source) != len(target) or len(source) < 2:
        raise ValueError('동일 개수의 대응점이 두 개 이상 필요합니다.')
    n = len(source)
    a = tuple(sum(p[k] for p in source)/n for k in (0, 1))
    b = tuple(sum(p[k] for p in target)/n for k in (0, 1))
    dot = cross = spread = 0.0
    for p, q in zip(source, target):
        x, y = p[0]-a[0], p[1]-a[1]
        u, v = q[0]-b[0], q[1]-b[1]
        dot += x*u + y*v
        cross += x*v - y*u
        spread += x*x + y*y
    if spread < 1e-12 or math.hypot(dot, cross) < 1e-12:
        raise ValueError('회전을 결정할 수 없는 점 배치입니다.')
    yaw = math.atan2(cross, dot)
    ra = transform(a, yaw, 0, 0)
    return yaw, b[0]-ra[0], b[1]-ra[1]


def candidates(map_a, map_b):
    """ID/정답을 받지 않고 위치와 class만 받는 후보 생성 인터페이스."""
    return [(i, j) for i, a in enumerate(map_a)
            for j, b in enumerate(map_b) if a['class'] == b['class']]


def make_maps(seed, extras, sigma):
    rng = random.Random(seed)
    classes = ['tree', 'pole', 'car']
    a = [{'class': classes[i % 3], 'xy': [rng.uniform(-5, 5), rng.uniform(-5, 5)]}
         for i in range(10)]
    truth = (math.radians(30), 10.0, 5.0)
    # 난수를 항상 동일 개수 소비하여 조건 사이에 같은 기본 지도/잡음을 사용.
    b = []
    for i, obj in enumerate(a):
        x, y = transform(obj['xy'], *truth)
        b.append((i, {'class': obj['class'],
                      'xy': [x + sigma*rng.gauss(0, 1), y + sigma*rng.gauss(0, 1)]}))
    for k in range(extras):
        b.append((None, {'class': classes[k % 3],
                         'xy': [rng.uniform(3, 17), rng.uniform(-2, 12)]}))
    random.Random(seed + 10000).shuffle(b)
    gt_pairs = [(identity, j) for j, (identity, _) in enumerate(b) if identity is not None]
    return a, [obj for _, obj in b], gt_pairs, truth


def draw_svg(path, a, b, estimate):
    aligned = [{'class': p['class'], 'xy': transform(p['xy'], *estimate)} for p in a]
    panels = [('A: past map', [(a, 'A', False)]),
              ('B: current map', [(b, 'B', False)]),
              ('Oracle alignment (NOT matched result)', [(b, 'B', False), (aligned, 'A', True)])]
    all_points = [p['xy'] for group in (a, b, aligned) for p in group]
    xmin = min(p[0] for p in all_points)-1
    xmax = max(p[0] for p in all_points)+1
    ymin = min(p[1] for p in all_points)-1
    ymax = max(p[1] for p in all_points)+1
    scale = min(320/(xmax-xmin), 300/(ymax-ymin))
    colors = {'tree': '#15803d', 'pole': '#2563eb', 'car': '#c2410c'}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="430" viewBox="0 0 1200 430">',
             '<rect width="1200" height="430" fill="white"/>']
    for k, (title, groups) in enumerate(panels):
        ox = 30 + 400*k
        parts.append(f'<text x="{ox}" y="25" font-family="sans-serif" font-size="15">{title}</text>')
        for group, prefix, hollow in groups:
            for i, p in enumerate(group):
                x = ox + (p['xy'][0]-xmin)*scale
                y = 355 - (p['xy'][1]-ymin)*scale
                color = colors[p['class']]
                fill = 'none' if hollow else color
                radius = 8 if hollow else 4
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{fill}" stroke="{color}" stroke-width="2"/>')
                if not hollow:
                    parts.append(f'<text x="{x+7:.2f}" y="{y-7:.2f}" font-family="sans-serif" font-size="11">{prefix}{i}</text>')
    parts.append('<text x="30" y="395" font-family="sans-serif" font-size="14">Green: tree | Blue: pole | Orange: car | Ring: transformed A | Same scale, coordinates in meters</text></svg>')
    path.write_text('\n'.join(parts), encoding='utf-8')


def run(seed, extras, sigma, directory=None):
    a, b, gt, truth = make_maps(seed, extras, sigma)
    proposed = candidates(a, b)
    correct = len(set(proposed) & set(gt))
    # Oracle: 정답 대응으로 변환 계산 코드만 검증합니다.
    estimate = estimate_transform([a[i]['xy'] for i, _ in gt], [b[j]['xy'] for _, j in gt])
    angle_error = abs(math.degrees(math.atan2(math.sin(estimate[0]-truth[0]), math.cos(estimate[0]-truth[0]))))
    row = dict(seed=seed, extra_objects=extras, noise_std_m=sigma,
               candidate_count=len(proposed), correct_candidates=correct,
               candidate_precision=correct/len(proposed) if proposed else 0.0,
               candidate_recall=correct/len(gt),
               oracle_translation_error_m=math.hypot(estimate[1]-truth[1], estimate[2]-truth[2]),
               oracle_yaw_error_deg=angle_error)
    if directory:
        directory.mkdir(parents=True, exist_ok=True)
        payload = dict(map_a=a, map_b=b, ground_truth_pairs=gt,
                       ground_truth_transform=dict(yaw_deg=30, tx=10, ty=5),
                       candidates=proposed, metrics=row)
        (directory/'maps.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
        draw_svg(directory/'maps.svg', a, b, estimate)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--trials', type=int, default=30)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'results')
    args = parser.parse_args()
    if args.trials < 1:
        parser.error('--trials must be positive')
    cases = [('clean', 0, 0.0), ('extra_2', 2, 0.0), ('extra_5', 5, 0.0),
             ('extra_10', 10, 0.0), ('noise_005', 0, 0.05),
             ('noise_010', 0, 0.10), ('noise_020', 0, 0.20)]
    rows = []
    for name, extras, sigma in cases:
        for trial in range(args.trials):
            row = run(args.seed+trial, extras, sigma, args.output/name if trial == 0 else None)
            rows.append(dict(condition=name, **row))
        first = rows[-args.trials]
        print(f"{name:12} candidates={first['candidate_count']:3} "
              f"precision={first['candidate_precision']:.3f} recall={first['candidate_recall']:.3f} "
              f"oracle_error={first['oracle_translation_error_m']:.6f}m / {first['oracle_yaw_error_deg']:.6f}deg")
    with (args.output/'metrics.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    # 기준 검증: 무잡음 복원, 모든 정답 보존, 후보 수 계산.
    for row in rows:
        assert row['candidate_recall'] == 1.0
        if row['noise_std_m'] == 0:
            assert row['oracle_translation_error_m'] < 1e-9
            assert row['oracle_yaw_error_deg'] < 1e-9
    assert rows[0]['candidate_count'] == 34
    print(f'PASS: clean transform recovery and candidate checks. Results: {args.output.resolve()}')
    print('IMPORTANT: oracle errors use ground-truth pairs; CLIPPER is not implemented.')


if __name__ == '__main__':
    main()
