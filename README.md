# Objective 2: newsvendor SP and RO experiments

本目录根据 proposal §2.2、公式 (9)–(11) 实现首轮可复现实验。原始 PDF 保留在本地研究目录。

## 运行

```powershell
python experiments\objective2_newsvendor.py --seeds 3 --n 40 --k 6 --time-limit 5
```

依赖：Python、NumPy、SciPy >= 1.9、Matplotlib。MILP 使用 SciPy/HiGHS。
默认结果写到 `results/objective2_newsvendor/`；重跑覆盖同一目录。

## 模型与数据

沿用已有报童原型的 tail-sensitive 成本：进货 2、销售收入 5、持有成本 0.05、缺货成本 4。
每个场景的总成本为 `2x - 5 min(x,d) + .05 max(x-d,0) + 4 max(d-x,0)`；最小化成本等于最大化利润。

干净需求是四成分混合正态，均值 160/200/240/290，标准差 8/10/8/5，概率 .24/.48/.24/.04，截断到 [120,305]。
训练集中固定两个合法尾部样本 285、300，确保每次都能检查真实极端事件的剔除行为。
这是 obj 2 新设计的合成数据实验，不是 proposal 已有结果的复现。

训练样本数 40，保留 6；污染率 0%、10%、20%；污染随机替换非固定尾部记录，使其需求增加 120–180。
外部质量标记模拟 80% 检出率与 3% 假阳性率。真实污染标签只用于评价和明确标出的 oracle 对照。
正常尾部标签仅在 protected 对照中用于约束；普通联合方法看不到该标签。

## 联合模型

- SP 距离是 41 个固定候选决策 `linspace(0,600,41)` 上 recourse 成本绝对差的均值。
- RO 距离是上述候选决策上单侧 recourse 成本差的最大值。
- 距离除以所有正距离的中位数，保证各次实验中的 lambda 使用可比较的尺度。导出的 RO bound 恢复原始成本单位。
- 使用连续 transport mass `pi`、二元 representative `z`、二元 exclusion `o`，完整实现行质量守恒、`pi_ij <= p_i z_j`、`pi_ii = p_i z_i`、支持数量和剔除质量预算。
- SP 最小化运输差异加剔除惩罚；RO 最小化 `t` 加剔除惩罚，并实现公式 (11) 的每行约束。
- 剔除质量上限为 20%。联合模型 lambda 为 .5/2/8（质量辅助），纯异常分数模型 lambda=2。
- 异常证据为 `max(d-320,0)/80`，剔除成本为 `clip(1/(1+score),.1,1)`；质量辅助模型对带标记记录再乘 .15。
- selected 场景的 transport 列质量先除以 retained mass，再用于 SP；RO 下游使用 selected 场景的最大成本。

## 对照方法

1. `full_observed`：污染后的全部训练数据。
2. `oracle_clean_full`：使用真实标签剔除污染，保留其余全部数据；仅是参考，不能部署。
3. `selection_only`：无剔除的决策感知选择。
4. `clean_then_select`：先按需求 >320 标记几何异常，最多剔除 20%，再做决策感知选择。
5. `joint_anomaly`：仅异常证据的联合剔除/选择。
6. `joint_quality`：异常证据与独立质量标记结合的联合模型。
7. `joint_quality_protected`：额外用真实合法尾部标签保护记录；oracle-assisted 消融对照。

## 评价与输出

- `runs.csv`：每次决策、独立干净评价成本/后悔、污染检出、合法尾部保留率、求解状态、MIP gap、耗时、RO bound。
- `summary.csv`：按方法/污染率/框架汇总三个随机种子，报告均值和种子间标准差。
- `scenario_details.json`：完整训练数据、污染/质量/尾部标签及选择与剔除索引。
- `config.json`：本次运行参数。
- `clean_regret.png`、`REPORT.md`：图和初步结果表。

干净 SP 用独立 10000 个场景评价，参考决策是其精确加权分位数。
干净 RO 用独立干净样本加已知域端点 120/305 评价，参考决策为端点成本交点。
RO 在本模型中需求成本凸，因此端点确实给出整个干净需求区间的最坏成本。
同时记录污染后全部训练场景的最坏成本，避免把删除后的低成本误认为对原数据仍有保护。

## 解释限制

这是先导实验；不能据此宣称新方法优于先清洗，也不能推出 blending 性能。
当前使用固定决策集合，尚未实现迭代候选决策更新。RO bound 只保证非剔除场景在已检查决策处的低估上界，另外记录下游决策处的实际低估。
每个 MILP 有 5 秒时间限制、1% 目标 gap；达到时限的可行 incumbent 不是已证明最优解，必须连同实际 gap 解读结果。
报童允许缺货罚款，有完整 recourse，因此没有独立的物理可行性约束；该实验不能检验 blending 的可行性保护。
污染只使用较易区分的大幅正偏移；之后应增加与真实尾部重叠的污染、质量标记误差敏感性、N/K 敏感性和更多种子。


## 绘图功能

主程序完成实验后自动调用 `experiments/plot_objective2.py`，输出后悔值、剔除数、MIP gap 热力图，以及均值和标准差对比图。

已有结果可以单独绘图，无需重新求解：

```powershell
python experiments/plot_objective2.py results/objective2_newsvendor/runs.csv --output results/objective2_newsvendor/plots
```

主程序也保留兼容入口：

```powershell
python experiments/objective2_newsvendor.py --plot-input results/objective2_newsvendor/runs.csv
```

实验可使用 `--output` 指定独立输出目录，避免覆盖已有结果。支持 CSV 和控制台日志文本；日志中的数字经过舍入，优先使用原始 CSV。

运行模型核验：

```powershell
python experiments/validate_objective2.py
```

## 连续熵约束版本与统一对比

新增三个脚本：

- `experiments/entropy_models.py`：连续熵模型、局部求解、多起点、支持集提取和 LP 重拟合。
- `experiments/run_entropy.py`：统一运行数据和参数相同的 MILP 与三个连续配置。
- `experiments/compare_entropy.py`：已有结果汇总与作图，无需求解模型。

配置含义：`partial` 对 z 加熵约束、允许连续部分删除；`double` 同时对 z/o 加熵约束；`continuation` 逐步收紧 z/o 熵容差。三者均用连续 SLSQP，不在内部调用整数求解器。
MILP 对照独立使用原有代码，沿用相同数据、质量标记、lambda、剔除预算、成本尺度与 SP/RO 评价集。

```powershell
python experiments/run_entropy.py --variant all --n 20 --k 4 --seeds 3 --epsilon-h 0.01 --epsilon-o 0.1 --starts 3 --time-limit 10
python experiments/run_entropy.py --variant double --epsilon-h 0 --epsilon-o 0 --output results/entropy_zero
python experiments/compare_entropy.py results/entropy_comparison/runs.csv
```

`--epsilon-h` 是 Objective 1 的质量熵容差；代码使用 `H(z) <= N * epsilon_h`，而 `H_bin(o) <= epsilon_o` 不乘 N。对数为自然对数，`0 log 0 = 0`；实际熵值按精确表达式检查，导数在端点附近截断到 1e-12 以便局部求解。原约束全部保留，内部使用 `a_ij = pi_ij / p_i` 改善数值尺度，输出 JSON 恢复为 pi。

`runs.csv` 明确区分 `raw` 与 `repaired`：前者保留连续解，后者按 z 排序取 K 个代表，对 o>0.5 的非代表按数值排序、在预算内作硬删除，再固定 z/o 用 LP 重拟合运输。因此 repaired 是公平比较硬支持集的一种确定规则，并非连续模型的精确最优恢复。记录支持数、分数 z/o 数、剔除质量、污染与合法质量删除、尾部保留、熵、可行性、耗时和后悔值；`details.json` 保存 z、o、pi、每次局部求解状态及 continuation 轨迹。

SLSQP 仅返回局部候选，没有全局 gap；熵为零仍保留组合难度，不保证能离开硬初始点。多起点包括无熵 LP 解及不使用真实标签构造的硬支持 LP 解，硬解可作为明确记录的 fallback。正容差也不能保证刚好 K 个非零支持。raw RO 使用全部正运输质量支持，不能当成 K 场景 RO 保证；原 proposal 的硬选择保护结论不直接适用于分数 z/o。

时间限制在 SLSQP 迭代边界检查，包含多起点与修复；不是操作系统级硬上限，矩阵构造、LP 和单次迭代可能导致超时。MILP 时间限制仅限制其求解阶段，耗时列包含外围开销，不能据此宣称预算严格一致。原始模型与历史结果保留。

`results/entropy_pilot/` 是 N=10、K=3、两个随机种子的运行与绘图验证，非正式算法优劣结论；正式比较应增加样本量、种子、容差敏感性与求解预算。
