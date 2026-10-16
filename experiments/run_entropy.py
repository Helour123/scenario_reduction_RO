"""Run continuous entropy variants and a matched MILP baseline."""
import argparse
import csv
import json
import time
from pathlib import Path
import numpy as np
if __package__:
    from .entropy_models import solve,decision
    from .objective2_newsvendor import sample,select,optimize,total
else:
    from entropy_models import solve,decision
    from objective2_newsvendor import sample,select,optimize,total


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=['all','partial','double','continuation'],default='all')
    p.add_argument('--n',type=int,default=20);p.add_argument('--k',type=int,default=4)
    p.add_argument('--seeds',type=int,default=3);p.add_argument('--lambda',dest='penalty',type=float,default=2.)
    p.add_argument('--epsilon-h',type=float,default=.01);p.add_argument('--epsilon-o',type=float,default=.1)
    p.add_argument('--starts',type=int,default=3);p.add_argument('--maxiter',type=int,default=100)
    p.add_argument('--time-limit',type=float,default=10.)
    p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'results/entropy_comparison')
    a=p.parse_args()
    if not 2<=a.n or not 1<=a.k<=a.n or min(a.seeds,a.starts,a.maxiter)<1 or a.time_limit<=0 or min(a.epsilon_h,a.epsilon_o,a.penalty)<0:p.error('Invalid parameters')
    a.output.mkdir(parents=True,exist_ok=True)
    variants=['partial','double','continuation'] if a.variant=='all' else [a.variant]
    rows=[];details=[]
    for seed in range(1000,1000+a.seeds):
      for rate in [0.,.1,.2]:
        d,clean,bad,flags,tail,test=sample(seed,a.n,rate)
        for robust in [False,True]:
          fw='RO' if robust else 'SP';ref=np.r_[test,120.,305.] if robust else test
          _,benchmark=optimize(ref,np.ones(len(ref))/len(ref),robust)
          def record(method,stage,x,seconds,extra):
            costs=total(x,ref).ravel();score=float(costs.max() if robust else costs.mean())
            rows.append(dict(seed=seed,contamination=rate,framework=fw,method=method,stage=stage,
                x=x,clean_regret=score-benchmark,clean_cost=score,seconds=seconds,**extra))
          started=time.perf_counter()
          x,sel,exc,info=select(d,a.k,robust,a.penalty,.2,'quality',flags,time_limit=a.time_limit)
          record('milp','hard',x,time.perf_counter()-started,dict(objective=info['representation_objective'],
            h_z=0.,h_o=0.,fractional_z=0,fractional_o=0,linear_violation=info['constraint_violation'],
            feasible=True,fallback=False,mip_gap=info['mip_gap'],support_size=int(sel.sum()),
            excluded_mass=float(exc.mean()),bad_removed_mass=float(np.mean(exc*bad)),
            valid_removed_mass=float(np.mean(exc*~bad)),tail_retention=float(np.mean(1-exc[tail]))))
          details.append(dict(seed=seed,rate=rate,framework=fw,method='milp',info=info,
            selected=np.flatnonzero(sel).tolist(),excluded=np.flatnonzero(exc).tolist()))
          for variant in variants:
            m,v,fixed,info=solve(d,a.k,robust,a.penalty,.2,flags,variant,a.epsilon_h,a.epsilon_o,
                a.starts,a.maxiter,a.time_limit,seed)
            n=len(d)
            for stage,vec in [('raw',v),('repaired',fixed)]:
                z=vec[m['z0']:m['o0']];o=vec[m['o0']:m['o0']+n]
                record(variant,stage,decision(m,vec,d),info['seconds'],dict(
                  objective=float(m['c']@vec),h_z=info['entropy_h'] if stage=='raw' else 0.,
                  h_o=info['entropy_o'] if stage=='raw' else 0.,
                  fractional_z=info['fractional_z'] if stage=='raw' else 0,
                  fractional_o=info['fractional_o'] if stage=='raw' else 0,
                  linear_violation=info['linear_violation'] if stage=='raw' else 0.,
                  feasible=info['feasible'],fallback=info['fallback'],mip_gap='',
                  support_size=int(np.sum(z>1e-8)),excluded_mass=float(o.mean()),
                  bad_removed_mass=float(np.mean(o*bad)),valid_removed_mass=float(np.mean(o*~bad)),
                  tail_retention=float(np.mean(1-o[tail]))))
            details.append(dict(seed=seed,rate=rate,framework=fw,method=variant,info=info,
                z=v[m['z0']:m['o0']].tolist(),o=v[m['o0']:m['o0']+n].tolist(),
                transport=(v[:n*n].reshape(n,n)/n).tolist(),
                repaired_z=fixed[m['z0']:m['o0']].tolist(),repaired_o=fixed[m['o0']:m['o0']+n].tolist(),
                demand=d.tolist(),bad=bad.tolist(),quality_flags=flags.tolist(),tail=tail.tolist()))
            print(f'{fw} seed={seed} rate={rate} {variant} feasible={info["feasible"]} '
                  f'fractional z/o={info["fractional_z"]}/{info["fractional_o"]}',flush=True)
          with (a.output/'runs.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
          (a.output/'details.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
    (a.output/'config.json').write_text(json.dumps(vars(a),indent=2,default=str),encoding='utf-8')
    if __package__:from .compare_entropy import compare
    else:from compare_entropy import compare
    compare(a.output/'runs.csv',a.output)


if __name__=='__main__':main()
