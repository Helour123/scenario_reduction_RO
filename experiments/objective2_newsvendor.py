"""Objective 2, equations (9)-(11): controlled SP/RO pilot experiments.

Run: python experiments/objective2_newsvendor.py --seeds 3 --n 40 --time-limit 5
Requires numpy, scipy>=1.9, matplotlib. No commercial solver required.
"""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

if __package__:
    from .plot_objective2 import CONFIGS, load_results, plot_results
else:
    from plot_objective2 import CONFIGS, load_results, plot_results


def recourse(x, d):
    y = np.minimum(np.asarray(x)[..., None], np.asarray(d))
    return -5*y + .05*(np.asarray(x)[..., None]-y) + 4*(d-y)


def total(x, d):
    return 2*np.asarray(x)[..., None] + recourse(x, d)


def optimize(d, weights=None, robust=False):
    if robust:
        # Convex-in-demand loss: worst observations are the two endpoints.
        # Their affine losses intersect inside [min(d),max(d)].
        x=float((4*np.max(d)+5.05*np.min(d))/9.05)
        x=float(np.clip(x,0,600))
        return x,float(total(x,d).max())
    order=np.argsort(d); cumulative=np.cumsum(weights[order])
    index=min(int(np.searchsorted(cumulative,7/9.05)),len(d)-1)
    x=float(np.clip(d[order[index]],0,600))
    return x,float(total(x,d).ravel()@weights)


def sample(seed, n, contamination):
    rng = np.random.default_rng(seed)
    # Explicit synthetic legitimate tail; labels are evaluation-only by default.
    comp = rng.choice(4, n, p=[.24, .48, .24, .04])
    clean = np.clip(rng.normal(np.array([160,200,240,290])[comp],
                               np.array([8,10,8,5])[comp]), 120, 305)
    comp[-2:] = 3
    clean[-2:] = [285.,300.]
    observed = clean.copy()
    bad = np.zeros(n, bool)
    count = round(n*contamination)
    if count:
        idx = rng.choice(np.arange(n-2), count, replace=False)
        bad[idx] = True
        observed[idx] += rng.uniform(120,180,count)
    # Imperfect external quality flag; not the true contamination label.
    flags = (rng.random(n) < np.where(bad,.8,.03))
    legitimate_tail = (comp==3) & ~bad
    # Independent clean evaluation sample, bounded to the specified domain.
    cr = rng.choice(4, 10000, p=[.24,.48,.24,.04])
    test = np.clip(rng.normal(np.array([160,200,240,290])[cr],
                              np.array([8,10,8,5])[cr]),120,305)
    return observed, clean, bad, flags, legitimate_tail, test


def select(d, k, robust, penalty, budget, mode, flags, protected=None,
           fixed_excluded=None, time_limit=5):
    n=len(d); p=np.full(n,1/n)
    # Fixed decision grid spans feasible domain; no oracle/test information.
    grid=np.linspace(0,600,41)
    responses=recourse(grid,d)
    if robust:
        distances=np.maximum((responses[:,:,None]-responses[:,None,:]).max(axis=0),0)
    else:
        distances=np.abs(responses[:,:,None]-responses[:,None,:]).mean(axis=0)
    scale=max(float(np.median(distances[distances>0])),1.)
    distances=distances/scale
    # Probability-mass transportation pi, representative z, exclusion o, RO t.
    z0=n*n; o0=z0+n; t0=o0+n; nv=t0+int(robust)
    c=np.zeros(nv)
    if robust: c[t0]=1
    else: c[:n*n]=distances.ravel()
    anomaly=np.maximum(d-320,0)/80
    out_cost=np.clip(1/(1+anomaly),.1,1.)
    if mode=='quality': out_cost*=np.where(flags,.15,1.)
    c[o0:o0+n]=penalty*p*out_cost
    lb=np.zeros(nv); ub=np.full(nv,np.inf)
    ub[:n*n]=np.repeat(p,n); ub[z0:t0]=1
    if protected is not None: ub[o0:o0+n][protected]=0
    if fixed_excluded is not None:
        lb[o0:o0+n]=fixed_excluded.astype(float)
        ub[o0:o0+n]=fixed_excluded.astype(float)
        ub[z0:z0+n][fixed_excluded]=0
    # mass n, capacity n*n, representative self mass n, cardinality, budget, RO n.
    nr=n+n*n+n+2+(n if robust else 0)
    A=lil_matrix((nr,nv)); lo=np.full(nr,-np.inf); hi=np.full(nr,np.inf); r=0
    for i in range(n):
        A[r,i*n:(i+1)*n]=1; A[r,o0+i]=p[i]; lo[r]=hi[r]=p[i]; r+=1
    for i in range(n):
        for j in range(n):
            A[r,i*n+j]=1; A[r,z0+j]=-p[i]; hi[r]=0; r+=1
    for i in range(n):
        A[r,i*n+i]=1; A[r,z0+i]=-p[i]; lo[r]=hi[r]=0; r+=1
    A[r,z0:z0+n]=1; lo[r]=hi[r]=k; r+=1
    A[r,o0:o0+n]=p; hi[r]=budget; r+=1
    if robust:
        for i in range(n):
            A[r,i*n:(i+1)*n]=distances[i]; A[r,t0]=-p[i]; hi[r]=0; r+=1
    integrality=np.zeros(nv); integrality[z0:t0]=1
    start=time.perf_counter()
    res=milp(c,integrality=integrality,bounds=Bounds(lb,ub),
             constraints=LinearConstraint(A.tocsr(),lo,hi),
             options={'time_limit':time_limit,'mip_rel_gap':.01})
    elapsed=time.perf_counter()-start
    if res.x is None: raise RuntimeError(f'No feasible incumbent: {res.message}')
    a=A.tocsr()@res.x
    violation=max(np.maximum(lo-a,0).max(),np.maximum(a-hi,0).max(),
                  np.maximum(lb-res.x,0).max(),np.maximum(res.x-ub,0).max(),
                  np.abs(res.x[z0:t0]-np.round(res.x[z0:t0])).max())
    if violation>1e-5: raise AssertionError(f'Infeasible incumbent {violation}')
    selected=res.x[z0:z0+n]>.5; excluded=res.x[o0:o0+n]>.5
    pi=res.x[:n*n].reshape(n,n)
    weights=pi.sum(axis=0)[selected]; weights/=weights.sum()
    if selected.sum()!=k or np.any(selected & excluded): raise AssertionError('Invalid support')
    x,_=optimize(d[selected],weights,robust)
    # For RO verify bound at grid AND at downstream decision (not general guarantee).
    t=float(res.x[t0]*scale) if robust else float('nan')
    if robust:
        bound_error=(responses[:,~excluded].max(axis=1)-responses[:,selected].max(axis=1)).max()
        # Row feasibility is measured in probability * normalized-cost units.
        # Convert the MILP feasibility tolerance before comparing raw costs.
        bound_tolerance=1e-4 + 1e-6*scale/float(p.min())
        if bound_error>t+bound_tolerance:
            raise AssertionError(f'Checked-decision bound violated: {bound_error} > {t} + {bound_tolerance}')
        downstream_under=max(0.,float(total(x,d[~excluded]).max()-total(x,d[selected]).max()))
    else: downstream_under=float('nan')
    return x,selected,excluded,dict(selection_seconds=elapsed,solver_status=int(res.status),
        mip_gap=float(res.mip_gap),constraint_violation=float(violation),
        representation_objective=float(res.fun),ro_bound=t,downstream_underestimate=downstream_under)


def run(args):
    output=args.output or Path(__file__).resolve().parents[1]/'results'/'objective2_newsvendor'
    output.mkdir(parents=True,exist_ok=True)
    rows=[]; details=[]
    for seed in range(args.seeds):
      for rate in [0.,.1,.2]:
        d,clean,bad,flags,tail,test=sample(1000+seed,args.n,rate)
        for robust in [False,True]:
          framework='RO' if robust else 'SP'
          reference=np.r_[test,120.,305.] if robust else test
          ref_x,ref_value=optimize(reference,np.full(len(reference),1/len(reference)),robust)
          configurations=[(method, penalty) for method, penalty, _ in CONFIGS]
          for method,penalty in configurations:
            start=time.perf_counter()
            if penalty is None:
                sel=np.ones(len(d),bool) if method=='full_observed' else ~bad
                exc=~sel
                x,_=optimize(d[sel],np.full(sel.sum(),1/sel.sum()),robust)
                info=dict(selection_seconds=0.,solver_status=0,mip_gap=0.,constraint_violation=0.,
                          representation_objective=float('nan'),ro_bound=float('nan'),
                          downstream_underestimate=float('nan'))
            else:
                # Sequential baseline uses geometry only; no quality flags.
                fixed=None
                if method=='clean_then_select':
                    fixed=np.zeros(len(d),bool)
                    candidates=np.flatnonzero(d>320)
                    candidates=candidates[np.argsort(d[candidates])[::-1]]
                    fixed[candidates[:int(np.floor(.2*len(d)+1e-8))]]=True
                budget=0. if method=='selection_only' else .2
                # Protection is an explicitly oracle-assisted ablation, not deployable.
                protected=tail if method=='joint_quality_protected' else None
                x,sel,exc,info=select(d,args.k,robust,penalty,budget,
                    'quality' if 'quality' in method else 'anomaly',flags,protected,fixed,args.time_limit)
            vals=total(x,reference).ravel()
            score=float(vals.max() if robust else vals.mean())
            tp=int((exc & bad).sum()); fp=int((exc & ~bad).sum())
            row=dict(seed=1000+seed,contamination=rate,framework=framework,method=method,
                lambda_=penalty if penalty is not None else '',x=x,reference_x=ref_x,
                clean_cost=score,clean_regret=score-ref_value,
                clean_mean_cost=float(total(x,test).mean()),
                clean_worst_cost=float(total(x,np.r_[test,120.,305.]).max()),
                observed_worst_cost=float(total(x,d).max()),
                excluded_count=int(exc.sum()),true_positive=tp,false_positive=fp,
                precision=tp/int(exc.sum()) if exc.sum() else float('nan'),
                recall=tp/int(bad.sum()) if bad.sum() else float('nan'),
                valid_tail_not_excluded=float((tail & ~exc).sum()/tail.sum()),
                valid_tail_selected=float((tail & sel).sum()/tail.sum()),
                support_size=int(sel.sum()),total_seconds=time.perf_counter()-start,**info)
            rows.append(row)
            details.append(dict(seed=1000+seed,rate=rate,framework=framework,method=method,
                penalty=penalty,demand=d.tolist(),latent_clean=clean.tolist(),bad=bad.tolist(),
                quality_flags=flags.tolist(),tail=tail.tolist(),selected=np.flatnonzero(sel).tolist(),
                excluded=np.flatnonzero(exc).tolist()))
            with (output/'runs.csv').open('w',newline='',encoding='utf-8-sig') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
            print(f'{framework} seed={seed} rate={rate} {method} lambda={penalty} '
                  f'regret={row["clean_regret"]:.3f} excluded={exc.sum()} gap={info["mip_gap"]:.3g}',flush=True)
    (output/'scenario_details.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
    (output/'config.json').write_text(json.dumps(vars(args),indent=2,default=str),encoding='utf-8')
    summary=[]
    for framework in ['SP','RO']:
      for rate in [0.,.1,.2]:
        for method,penalty in configurations:
            rr=[r for r in rows if r['framework']==framework and r['contamination']==rate and
                r['method']==method and r['lambda_']==(penalty if penalty is not None else '')]
            v=np.array([r['clean_regret'] for r in rr])
            summary.append(dict(framework=framework,contamination=rate,method=method,lambda_=penalty,
                mean_regret=float(v.mean()),std_regret=float(v.std(ddof=1)) if len(v)>1 else 0.,
                mean_tail_retention=float(np.mean([r['valid_tail_not_excluded'] for r in rr])),
                mean_seconds=float(np.mean([r['total_seconds'] for r in rr])),
                mean_mip_gap=float(np.mean([r['mip_gap'] for r in rr]))))
    with (output/'summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    plot_files=plot_results(rows, output, 'Generated experiment rows')
    lines=['# Objective 2 newsvendor pilot results','',
        f'{len(rows)} runs; {args.seeds} seeds; N={args.n}; K={args.k}.',
        '','Costs are minimized (negative profit). Regret uses independent clean data.',
        'RO clean evaluation additionally includes demand-domain endpoints 120 and 305.',
        'Error bars show across-seed standard deviation, not confidence intervals.',
        '','Generated plots: ' + ', '.join(path.name for path in plot_files) + '.',
        '','| Framework | Contamination | Method | Lambda | Mean regret | SD | Tail retained | Mean MIP gap |',
        '|---|---|---|---|---|---|---|---|']
    for r in summary:
        lines.append(f'| {r["framework"]} | {r["contamination"]} | {r["method"]} | {r["lambda_"]} | '
                     f'{r["mean_regret"]:.3f} | {r["std_regret"]:.3f} | {r["mean_tail_retention"]:.1%} | {r["mean_mip_gap"]:.3g} |')
    lines+=['','Limitations: pilot synthetic data; external flags simulated; protected-tail and oracle-clean methods use oracle labels; '
            'candidate decisions fixed; no adaptive updates; time-limited MILP incumbents may not be optimal. '
            'RO guarantee applies only to non-excluded scenarios at the checked decision grid. '
            'Newsvendor has complete recourse, so this experiment does not assess uncertain-constraint feasibility. '
            'No conclusion about blending can be drawn from this pilot.']
    (output/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot-input',type=Path,default=None,
                        help='Existing runs.csv or console-log .txt to plot without rerunning optimization')
    parser.add_argument('--plot-output',type=Path,default=None,
                        help='Output directory for --plot-input; defaults to input parent / plots')
    parser.add_argument('--output',type=Path,default=None,help='Experiment output directory')
    parser.add_argument('--seeds',type=int,default=3)
    parser.add_argument('--n',type=int,default=40)
    parser.add_argument('--k',type=int,default=6)
    parser.add_argument('--time-limit',type=float,default=5.)
    args=parser.parse_args()
    if args.plot_input is not None:
        note='CSV results' if args.plot_input.suffix.lower()=='.csv' else 'Rounded console-log values'
        output=args.plot_output or args.plot_input.parent/'plots'
        for path in plot_results(load_results(args.plot_input), output, note):
            print(path.resolve())
        raise SystemExit(0)
    if not 1<=args.k<=args.n or args.seeds<1: parser.error('Invalid sizes')
    run(args)
