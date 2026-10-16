"""Aggregate entropy/MILP results; keep raw and repaired stages separate."""
import argparse
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def compare(source,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader(Path(source).open(encoding='utf-8-sig')))
    groups={}
    for r in rows:groups.setdefault((r['framework'],r['contamination'],r['method'],r['stage']),[]).append(r)
    summary=[]
    for (fw,rate,method,stage),rr in groups.items():
        vals=np.array([float(r['clean_regret']) for r in rr])
        summary.append(dict(framework=fw,contamination=float(rate),method=method,stage=stage,
          seeds=len(rr),mean_regret=float(vals.mean()),sd_regret=float(vals.std(ddof=1)) if len(rr)>1 else 0.,
          mean_seconds=float(np.mean([float(r['seconds']) for r in rr])),
          mean_fractional_z=float(np.mean([float(r['fractional_z']) for r in rr])),
          mean_fractional_o=float(np.mean([float(r['fractional_o']) for r in rr])),
          feasible_count=sum(r['feasible']=='True' for r in rr),fallback_count=sum(r['fallback']=='True' for r in rr)))
    with (output/'summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    for stage in ['raw','repaired']:
        fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
        for ax,fw in zip(axes,['SP','RO']):
            for method in dict.fromkeys(r['method'] for r in summary):
                rr=sorted([r for r in summary if r['framework']==fw and r['method']==method and r['stage'] in [stage,'hard']],key=lambda r:r['contamination'])
                if rr:ax.errorbar([r['contamination'] for r in rr],[r['mean_regret'] for r in rr],
                    yerr=[r['sd_regret'] for r in rr],marker='o',capsize=3,label=method)
            ax.set(title=fw,xlabel='Contamination',ylabel='Clean decision regret');ax.grid(alpha=.2);ax.legend()
        fig.suptitle(f'{stage}: mean +/- sample SD; local entropy candidates, not global optima')
        fig.savefig(output/f'comparison_{stage}.png',dpi=160);plt.close(fig)
    lines=['# Continuous entropy / MILP comparison','',
      'Raw and repaired results have different meanings. Repaired results use exactly K hard representatives and hard deletion, with LP transport refit.',
      'Raw partial deletion changes the model. Raw RO includes every positive-weight support; fractional selection does not imply K scenarios.',
      'Seconds include entropy multistart and hard repair; SLSQP time limits are cooperative. MILP gaps are in runs.csv. No global bound exists for local entropy runs.',
      'Zero entropy tolerances preserve the discrete feasible set. Failed local solves do not prove infeasibility; feasible hard LP starts may be returned.',
      '','| Framework | Contamination | Method | Stage | Mean regret | SD | Seconds | Fractional z/o | Fallbacks |',
      '|---|---|---|---|---|---|---|---|---|']
    for r in summary:lines.append(f'| {r["framework"]} | {r["contamination"]:.0%} | {r["method"]} | {r["stage"]} | {r["mean_regret"]:.3f} | {r["sd_regret"]:.3f} | {r["mean_seconds"]:.2f} | {r["mean_fractional_z"]:.1f}/{r["mean_fractional_o"]:.1f} | {r["fallback_count"]} |')
    (output/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();compare(a.input,a.output or a.input.parent)
