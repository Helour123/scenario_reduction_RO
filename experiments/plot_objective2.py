"""Plot existing Objective 2 CSV results or console logs without solving models."""
import argparse
import csv
import re
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CONFIGS = [
    ('full_observed', None, 'Full observed'),
    ('oracle_clean_full', None, 'Oracle clean (true labels)'),
    ('selection_only', 2., 'Selection only'),
    ('clean_then_select', 2., 'Clean then select'),
    ('joint_anomaly', 2., 'Joint anomaly | lambda=2'),
    ('joint_quality', .5, 'Joint quality | lambda=0.5'),
    ('joint_quality', 2., 'Joint quality | lambda=2'),
    ('joint_quality', 8., 'Joint quality | lambda=8'),
    ('joint_quality_protected', 2., 'Protected tail (oracle) | lambda=2'),
]


def normalize_rows(rows):
    out = []
    for r in rows:
        penalty = r.get('lambda_', r.get('penalty'))
        penalty = None if penalty in (None, '', 'None') else float(penalty)
        out.append(dict(framework=r['framework'], seed=int(r['seed']),
                        contamination=float(r['contamination']), method=r['method'],
                        lambda_=penalty, clean_regret=float(r['clean_regret']),
                        excluded_count=int(r['excluded_count']), mip_gap=float(r['mip_gap'])))
    if not out:
        raise ValueError('No experiment records found.')
    keys = [(r['framework'], r['seed'], r['contamination'], r['method'], r['lambda_']) for r in out]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate records: provide one experiment run at a time.')
    return out


def load_results(path):
    path = Path(path)
    if path.suffix.lower() == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as f:
            return normalize_rows(list(csv.DictReader(f)))
    pattern = re.compile(
        r'^(SP|RO) seed=(\d+) rate=([\d.eE+-]+) (\w+) lambda=(None|[\d.eE+-]+) '
        r'regret=([\d.eE+-]+) excluded=(\d+) gap=([\d.eE+-]+)\s*$', re.M)
    rows = []
    for framework, seed, rate, method, penalty, regret, excluded, gap in pattern.findall(
            path.read_text(encoding='utf-8-sig')):
        seed = int(seed)
        if seed < 1000:
            seed += 1000
        rows.append(dict(framework=framework, seed=seed, contamination=rate, method=method,
                         lambda_=penalty, clean_regret=regret, excluded_count=excluded, mip_gap=gap))
    return normalize_rows(rows)


def plot_results(rows, output, source_note='Full-precision experiment rows'):
    """Save annotated heatmaps and a mean +/- sample-SD regret plot."""
    rows = normalize_rows(rows)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rates = sorted({r['contamination'] for r in rows})
    frameworks = [f for f in ('SP', 'RO') if any(r['framework'] == f for r in rows)]
    configs = [c for c in CONFIGS if any(r['method'] == c[0] and r['lambda_'] == c[1] for r in rows)]
    grouped = {}
    for r in rows:
        grouped.setdefault((r['framework'], r['method'], r['lambda_'], r['contamination']), []).append(r)
    summaries = []
    for (f, method, penalty, rate), rr in grouped.items():
        regrets = np.array([r['clean_regret'] for r in rr])
        summaries.append(dict(framework=f, method=method, lambda_=penalty,
                              contamination=rate, seeds=len(rr), mean_regret=regrets.mean(),
                              sd_regret=regrets.std(ddof=1) if len(rr) > 1 else float('nan'),
                              mean_excluded=np.mean([r['excluded_count'] for r in rr]),
                              mean_mip_gap=np.mean([r['mip_gap'] for r in rr]) if penalty is not None else float('nan')))
    with (output / 'plot_summary.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.facecolor': 'white'})
    metrics = [
        ('clean_regret', 1., 'Mean clean decision regret', 'regret_heatmap.png', 'YlOrRd'),
        ('excluded_count', 1., 'Mean number of excluded scenarios', 'exclusion_heatmap.png', 'Blues'),
        ('mip_gap', 100., 'Mean relative MIP gap (%)', 'gap_heatmap.png', 'Purples'),
    ]
    counts = sorted({len(g) for g in grouped.values()})
    count_text = str(counts[0]) if len(counts) == 1 else f'{min(counts)}-{max(counts)}'
    files = []
    for metric, multiplier, title, name, cmap in metrics:
        fig, axes = plt.subplots(1, len(frameworks), figsize=(16, 6.8), squeeze=False,
                                 layout='constrained')
        for ax, framework in zip(axes[0], frameworks):
            values = np.full((len(configs), len(rates)), np.nan)
            for i, (method, penalty, _) in enumerate(configs):
                for j, rate in enumerate(rates):
                    rr = grouped.get((framework, method, penalty, rate), [])
                    if rr and not (metric == 'mip_gap' and penalty is None):
                        values[i, j] = multiplier * np.mean([r[metric] for r in rr])
            vmax = max(float(np.nanmax(values)), 1.) if np.isfinite(values).any() else 1.
            im = ax.imshow(np.ma.masked_invalid(values), cmap=cmap, vmin=0, vmax=vmax, aspect='auto')
            ax.set_xticks(range(len(rates)), [f'{r:.0%}' for r in rates])
            ax.set_yticks(range(len(configs)), [c[2] for c in configs])
            ax.set_xlabel('Contamination fraction')
            ax.set_title(framework + (' | expected-cost regret' if framework == 'SP' else ' | worst-cost regret')
                         if metric == 'clean_regret' else framework, fontweight='bold', pad=12)
            for i in range(len(configs)):
                for j in range(len(rates)):
                    v = values[i, j]
                    label = 'N/A' if not np.isfinite(v) else f'{v:.2f}'
                    ax.text(j, i, label, ha='center', va='center',
                            color='white' if np.isfinite(v) and v > .6*vmax else '#17212b')
            fig.colorbar(im, ax=ax, fraction=.035, pad=.03)
        suffix = 'Separate SP/RO color scales; smaller is better.' if metric == 'clean_regret' else (
            'Counts alone do not identify true or false exclusions.' if metric == 'excluded_count' else
            'Gap concerns the selection MILP objective, not clean regret. Baselines: N/A.')
        fig.suptitle(f'{title}\n{count_text} seeds per available cell | {source_note}\n{suffix}', fontsize=13)
        fig.savefig(output / name, dpi=180)
        plt.close(fig)
        files.append(output / name)

    fig, axes = plt.subplots(1, len(frameworks), figsize=(14, 6), squeeze=False, layout='constrained')
    colors = plt.get_cmap('tab10').colors
    for ax, framework in zip(axes[0], frameworks):
        for ci, (method, penalty, label) in enumerate(configs):
            means, sds = [], []
            for rate in rates:
                rr = grouped.get((framework, method, penalty, rate), [])
                vv = np.array([r['clean_regret'] for r in rr])
                means.append(vv.mean() if len(vv) else np.nan)
                sds.append(vv.std(ddof=1) if len(vv) > 1 else np.nan)
            ax.errorbar(np.array(rates)*100, means, yerr=sds, color=colors[ci % 10],
                        marker='o', markersize=4, capsize=3, linewidth=1.3,
                        linestyle='--' if 'oracle' in method or 'protected' in method else '-', label=label)
        ax.set(title=framework, xlabel='Contamination (%)', ylabel='Clean decision regret')
        ax.set_xticks(np.array(rates)*100)
        ax.grid(alpha=.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncol=3, fontsize=9)
    fig.suptitle('Clean regret: mean +/- sample standard deviation (not confidence intervals)\n'
                 f'{count_text} seeds per available cell | {source_note}', fontsize=12)
    fig.savefig(output / 'regret_with_sd.png', dpi=180)
    fig.savefig(output / 'clean_regret.png', dpi=180)
    plt.close(fig)
    files.append(output / 'regret_with_sd.png')
    files.append(output / 'clean_regret.png')
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='runs.csv or console-log .txt')
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    note = 'CSV results' if args.input.suffix.lower() == '.csv' else 'Rounded console-log values'
    for path in plot_results(load_results(args.input), args.output or args.input.parent/'plots', note):
        print(path.resolve())
