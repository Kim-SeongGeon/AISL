"""Official CLIPPER solve via C++ adapter, followed by 2D pose and GT evaluation."""
import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from experiment import estimate_transform

ROOT = Path(__file__).resolve().parent.parent

def select(a, b, candidates, epsilon, sigma):
    # The subprocess receives coordinates and candidate indices only, never GT.
    lines = [f'{len(a)} {len(b)} {len(candidates)} {epsilon} {sigma}']
    lines += [f"{o['xy'][0]:.17g} {o['xy'][1]:.17g}" for o in a+b]
    lines += [f'{i} {j}' for i,j in candidates]
    data = '\n'.join(lines)+'\n'
    run = subprocess.run([str(ROOT/'build/clipper/clipper_driver')], input=data,
                         text=True, capture_output=True, check=True, timeout=30)
    values = list(map(int, run.stdout.split()))
    assert len(values) == 1+2*values[0]
    selected = list(zip(values[1::2], values[2::2]))
    assert set(selected) <= set(map(tuple,candidates))
    assert len({i for i,j in selected}) == len(selected)
    assert len({j for i,j in selected}) == len(selected)
    return selected, data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    # independent exact, permuted 3-4-5 triangle, class labels not required by adapter
    a=[{'xy':p} for p in [(0,0),(4,0),(0,3)]]
    b=[{'xy':p} for p in [(7,5),(10,5),(10,9)]]
    selected,_=select(a,b,[(i,j) for i in range(3) for j in range(3)],.05,.20)
    assert set(selected)=={(0,1),(1,2),(2,0)}, selected
    rows=[]
    for case in ['clean','extra_5','noise_020']:
        for epsilon in [.05,.20,.50]:
            source=ROOT/f'virtual_map/results_graph_macos_20260911/{case}_eps_{epsilon:.2f}/graph.json'
            p=json.loads(source.read_text())
            a,b,candidates=p['map_a'],p['map_b'],p['candidates']
            # Predeclared kernel scale fixed across all cases, not tuned with GT.
            sigma=.20
            selected,solver_input=select(a,b,candidates,epsilon,sigma)
            repeat,_=select(a,b,candidates,epsilon,sigma)
            assert selected==repeat, 'deterministic initial vector repeat check'
            # Check output pairs are mutually compatible by official threshold.
            for u,(i,j) in enumerate(selected):
                for k,l in selected[u+1:]:
                    delta=abs(math.dist(a[i]['xy'],a[k]['xy'])-math.dist(b[j]['xy'],b[l]['xy']))
                    weight=math.exp(-.5*(delta/sigma)**2)
                    assert delta<epsilon and weight>1e-4
            gt=set(map(tuple,p['evaluation_only']['ground_truth_pairs']))
            correct=len(set(selected)&gt)
            row=dict(condition=case,seed=42,epsilon_m=epsilon,kernel_sigma_m=sigma,
                     candidates=len(candidates),selected=len(selected),correct=correct,
                     precision=correct/len(selected) if selected else None,recall=correct/len(gt),
                     pose_status='not_enough_pairs',translation_error_m=None,yaw_error_deg=None)
            estimate=None
            if len(selected)>=2:
                try:
                    estimate=estimate_transform([a[i]['xy'] for i,j in selected],[b[j]['xy'] for i,j in selected])
                    yaw,tx,ty=estimate
                    row.update(pose_status='estimated',translation_error_m=math.hypot(tx-10,ty-5),
                               yaw_error_deg=abs(math.degrees(math.atan2(math.sin(yaw-math.pi/6),math.cos(yaw-math.pi/6)))))
                except ValueError as exc:
                    row['pose_status']=str(exc)
            if case!='noise_020':
                assert correct==len(selected)==10
                assert row['translation_error_m']<1e-9 and row['yaw_error_deg']<1e-9
            folder=args.output/f'{case}_eps_{epsilon:.2f}'
            folder.mkdir()
            (folder/'solver_input.txt').write_text(solver_input)
            (folder/'result.json').write_text(json.dumps(dict(selected_pairs=selected,estimate_A_to_B=estimate,
                 metrics=row,input_source=str(source.relative_to(ROOT)),input_sha256=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2))
            rows.append(row)
            print(json.dumps(row))
    with (args.output/'metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    files=['virtual_map/clipper_driver.cpp','virtual_map/clipper_experiment.py','virtual_map/build_clipper.sh',
           'virtual_map/experiment.py','build/clipper/clipper_driver']
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),
        argv=sys.argv,clipper_commit='e514dc29c273837ffdfeebbefbdcb2a93d970969',
        eigen_commit='3147391d946bb4b6c68edd901f2add6ac1f31f8c',clipper_version='0.2.4',
        solver='official CLIPPER::solve; default Params, DSD_HEU rounding; uniform ones u0, rescale_u0=true',
        kernel='delta < epsilon then exp(-0.5*delta^2/sigma^2); affinityeps=1e-4; mindist=0',
        kernel_sigma_m=.20,seed=42,trials_per_case=1,direction='A_to_B',position_unit='m',angle_output='deg',
        build='Apple clang 21.0.0; C++14 -O2; serial; no OpenMP/PMC/SCS/BLAS/MKL/Python bindings',
        hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
        checks=['independent permuted 3-4-5 triangle','repeatability','selection subset and one-to-one',
                'selected pairwise consistency','noise-free 10/10 and pose <1e-9'],
        limitations='single map seed and one initial vector; no timing benchmark or success-rate threshold; not SlideGraph or SLAM')
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__': main()
