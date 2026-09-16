"""Fixed-settings, 30-map CLIPPER evaluation; GT is evaluation only."""
import argparse, csv, hashlib, json, math, platform, statistics, sys
from datetime import datetime, timezone
from pathlib import Path
from experiment import make_maps, candidates, estimate_transform
from clipper_experiment import ROOT, select

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    old=json.loads((ROOT/'virtual_map/results_clipper_macos_20260914/manifest.json').read_text())
    for p,h in old['hashes'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:
            raise RuntimeError('Previous experiment code/binary changed: '+p)
    manifest=dict(old,created_at=datetime.now(timezone.utc).isoformat(),argv=sys.argv,
                  python=sys.version,platform=platform.platform(),seed=None,seeds=list(range(42,72)),
                  trials_per_case=30,planned_rows=270,status='running',
                  limitations='30 map seeds, fixed ones solver initialization; no success threshold, no place retrieval/SLAM evaluation')
    manifest['hashes']['virtual_map/clipper_sweep.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    dump(args.output/'manifest.json',manifest)
    rows=[]
    for case,extras,noise in [('clean',0,0),('extra_5',5,0),('noise_020',0,.2)]:
        for seed in range(42,72):
            a,b,gt,truth=make_maps(seed,extras,noise)
            proposed=candidates(a,b)
            for epsilon in [.05,.2,.5]:
                row=dict(condition=case,seed=seed,epsilon_m=epsilon,kernel_sigma_m=.2,
                         candidates=len(proposed),selected=None,correct=None,precision=None,recall=None,
                         pose_status='solver_error',translation_error_m=None,yaw_error_deg=None,
                         consistent=None,error=None)
                selected=[];estimate=None;solver_input=None
                try:
                    selected,solver_input=select(a,b,proposed,epsilon,.2)
                    row.update(selected=len(selected),correct=len(set(selected)&set(gt)),pose_status='not_enough_pairs')
                    row.update(precision=row['correct']/len(selected) if selected else None,recall=row['correct']/len(gt))
                    row['consistent']=all(abs(math.dist(a[i]['xy'],a[k]['xy'])-math.dist(b[j]['xy'],b[l]['xy']))<epsilon
                        and math.exp(-.5*(abs(math.dist(a[i]['xy'],a[k]['xy'])-math.dist(b[j]['xy'],b[l]['xy']))/.2)**2)>1e-4
                        for u,(i,j) in enumerate(selected) for k,l in selected[u+1:])
                    if len(selected)>=2:
                        try:
                            estimate=estimate_transform([a[i]['xy'] for i,j in selected],[b[j]['xy'] for i,j in selected])
                            yaw,tx,ty=estimate
                            row.update(pose_status='estimated',translation_error_m=math.hypot(tx-truth[1],ty-truth[2]),
                              yaw_error_deg=abs(math.degrees(math.atan2(math.sin(yaw-truth[0]),math.cos(yaw-truth[0])))))
                        except ValueError as exc: row.update(pose_status='degenerate',error=str(exc))
                except Exception as exc: row['error']=repr(exc)
                folder=args.output/f'{case}_seed_{seed}_eps_{epsilon:.2f}';folder.mkdir()
                dump(folder/'result.json',dict(metrics=row,map_a=a,map_b=b,candidates=proposed,
                     selected_pairs=selected,estimate_A_to_B=estimate,evaluation_only=dict(gt_pairs=gt,truth=truth)))
                if solver_input is not None: (folder/'solver_input.txt').write_text(solver_input)
                rows.append(row)
            if seed==71: print(case,'completed',flush=True)
    with (args.output/'metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    summaries=[]
    for case in ['clean','extra_5','noise_020']:
        for ep in [.05,.2,.5]:
            group=[r for r in rows if r['condition']==case and r['epsilon_m']==ep]
            s=dict(condition=case,epsilon_m=ep,n=len(group),estimated=sum(r['pose_status']=='estimated' for r in group),
                   solver_errors=sum(r['pose_status']=='solver_error' for r in group),
                   with_wrong_pairs=sum(r['selected'] is not None and r['selected']>r['correct'] for r in group),
                   inconsistent=sum(r['consistent'] is False for r in group))
            for key in ['selected','precision','recall','translation_error_m','yaw_error_deg']:
                vals=[r[key] for r in group if r[key] is not None]
                s[key]=dict(n=len(vals),mean=statistics.mean(vals) if vals else None,
                  sample_std=statistics.stdev(vals) if len(vals)>1 else None,
                  median=statistics.median(vals) if vals else None,max=max(vals) if vals else None)
            summaries.append(s)
    comparisons=[]
    for lo,hi in [(.05,.2),(.2,.5)]:
        pairs=[([r for r in rows if r['condition']=='noise_020' and r['seed']==seed and r['epsilon_m']==lo][0],
                [r for r in rows if r['condition']=='noise_020' and r['seed']==seed and r['epsilon_m']==hi][0]) for seed in range(42,72)]
        valid=[(a,b) for a,b in pairs if a['pose_status']==b['pose_status']=='estimated']
        more=[(a,b) for a,b in valid if b['selected']>a['selected']]
        comparisons.append(dict(epsilon_from=lo,epsilon_to=hi,valid_pairs=len(valid),more_selected=len(more),
           more_selected_but_worse_yaw=sum(b['yaw_error_deg']>a['yaw_error_deg']+1e-12 for a,b in more)))
    dump(args.output/'summary.json',dict(groups=summaries,noise_paired_comparisons=comparisons,
         aggregation='macro mean and sample SD per 30 seeds; pose stats use estimated rows only; missing counts retained'))
    manifest.update(status='completed',actual_rows=len(rows),checks=['prior code/binary hashes verified'],
                    finished_at=datetime.now(timezone.utc).isoformat())
    dump(args.output/'manifest.json',manifest)
    print(json.dumps(dict(groups=summaries,comparisons=comparisons)))

if __name__=='__main__': main()
