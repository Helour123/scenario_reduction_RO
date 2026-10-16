"""Independent small-instance checks against exhaustive selection/exclusion."""
import itertools
import numpy as np
from scipy.optimize import linprog
from objective2_newsvendor import select, recourse, optimize, total

d=np.array([145.,180.,210.,270.,300.,440.])
flags=np.array([False,False,False,False,False,True])
grid=np.linspace(0,600,41); response=recourse(grid,d)
for robust in [False,True]:
    distance=(np.maximum((response[:,:,None]-response[:,None,:]).max(axis=0),0)
              if robust else np.abs(response[:,:,None]-response[:,None,:]).mean(axis=0))
    distance/=np.median(distance[distance>0])
    cout=np.clip(1/(1+np.maximum(d-320,0)/80),.1,1)*np.where(flags,.15,1.)
    best=float('inf')
    for selected in itertools.combinations(range(len(d)),2):
        for excluded in [()]+[(i,) for i in range(len(d)) if i not in selected]:
            retained=[i for i in range(len(d)) if i not in excluded]
            residual=distance[np.ix_(retained,selected)].min(axis=1)
            # Selected representatives have self distance zero and keep own mass.
            matching=residual.max() if robust else residual.sum()/len(d)
            value=matching+.5*sum(cout[i] for i in excluded)/len(d)
            best=min(best,value)
    _,_,_,info=select(d,2,robust,.5,1/6,'quality',flags,time_limit=30)
    assert abs(info['representation_objective']-best)<1e-6,(robust,best,info)
    print(('RO' if robust else 'SP')+' MILP matches exhaustive optimum')

x,v=optimize(d,robust=True)
result=linprog([0,1],A_ub=[[2.05,-1],[-7,-1]],
               b_ub=[5.05*d.min(),-4*d.max()],bounds=[(0,600),(None,None)])
assert abs(x-result.x[0])<1e-7 and abs(v-result.fun)<1e-7
x,v=optimize(d,np.ones(len(d))/len(d))
assert v<=total(np.linspace(0,600,6001),d).mean(axis=1).min()+1e-7
print('Downstream SP quantile and RO LP checks passed')

# Continuous entropy identities, original-model scaling, and zero-tolerance case.
from entropy_models import entropy, binary_entropy, solve, build, lp, residual
z=np.array([1.,0.,.25,.75]);q=z/len(z)
assert abs(entropy(q)-(z.sum()*np.log(len(z))+entropy(z))/len(z))<1e-12
assert entropy(np.array([0.,1.]))==0 and binary_entropy(np.array([0.,1.]))==0
assert entropy(np.array([.5,.5]))>0
for robust in [False,True]:
    model=build(d,2,robust,.5,1/6,flags)
    selected=np.array([1.,0.,0.,0.,0.,1.]);excluded=np.zeros(len(d))
    v=lp(model,selected,excluded)
    assert residual(model,v)<1e-7
    m,raw,fixed,info=solve(d,2,robust,.5,1/6,flags,'double',0.,0.,
                         starts=2,maxiter=10,time_limit=2)
    assert info['feasible'] and info['fractional_z']==0 and info['fractional_o']==0
    assert residual(m,fixed)<1e-7
    assert abs(fixed[m['z0']:m['o0']].sum()-2)<1e-8
print('Entropy identity, boundary values, continuous zero-tolerance and repair checks passed')
