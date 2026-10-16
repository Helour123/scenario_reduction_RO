"""Continuous nonconvex alternatives to Objective 2 binary selection.

SLSQP with analytical derivatives and multiple LP-based starts. No MILP is
used inside the entropy solver. Feasibility is checked with exact x log x.
"""
import time
import numpy as np
from scipy.optimize import linprog, minimize, LinearConstraint, Bounds
from scipy.special import xlogy
from scipy.sparse import lil_matrix

if __package__:
    from .objective2_newsvendor import recourse, optimize
else:
    from objective2_newsvendor import recourse, optimize


def entropy(z):
    return float(-np.sum(xlogy(z,z)))


def binary_entropy(o):
    return entropy(o)+entropy(1-o)


def build(d,k,robust,penalty,budget,flags):
    n=len(d); z0=n*n; o0=z0+n; size=o0+n+int(robust)
    q=recourse(np.linspace(0,600,41),d)
    dist=np.maximum((q[:,:,None]-q[:,None,:]).max(0),0) if robust else np.abs(q[:,:,None]-q[:,None,:]).mean(0)
    positive=dist[dist>0]; scale=max(float(np.median(positive)),1.) if positive.size else 1.
    dist/=scale
    c=np.zeros(size)
    if robust:c[-1]=1
    else:c[:z0]=dist.ravel()/n
    cost=np.clip(1/(1+np.maximum(d-320,0)/80),.1,1)*np.where(flags,.15,1.)
    c[o0:o0+n]=penalty*cost/n
    # a_ij = pi_ij / p_i, equal p_i=1/n. This improves conditioning.
    eq=lil_matrix((2*n+1,size)); rhs=np.r_[np.ones(n),np.zeros(n),k]
    for i in range(n):
        eq[i,i*n:(i+1)*n]=1;eq[i,o0+i]=1
        eq[n+i,i*n+i]=1;eq[n+i,z0+i]=-1
    eq[-1,z0:o0]=1
    ub=lil_matrix((n*n+1+(n if robust else 0),size)); b=np.zeros(ub.shape[0])
    r=0
    for i in range(n):
        for j in range(n):ub[r,i*n+j]=1;ub[r,z0+j]=-1;r+=1
    ub[r,o0:o0+n]=1/n;b[r]=budget;r+=1
    if robust:
        for i in range(n):ub[r,i*n:(i+1)*n]=dist[i];ub[r,-1]=-1;r+=1
    upper=np.ones(size)
    if robust:upper[-1]=np.inf
    return dict(n=n,k=k,robust=robust,c=c,eq=eq.toarray(),rhs=rhs,
                ub=ub.toarray(),b=b,upper=upper,z0=z0,o0=o0,scale=scale,budget=budget)


def lp(model,z=None,o=None,objective=None):
    lo=np.zeros(len(model['c']));hi=model['upper'].copy();n=model['n']
    if z is not None:lo[model['z0']:model['o0']]=z;hi[model['z0']:model['o0']]=z
    if o is not None:lo[model['o0']:model['o0']+n]=o;hi[model['o0']:model['o0']+n]=o
    result=linprog(model['c'] if objective is None else objective,
        A_eq=model['eq'],b_eq=model['rhs'],A_ub=model['ub'],b_ub=model['b'],
        bounds=list(zip(lo,hi)),method='highs')
    if not result.success:raise RuntimeError(result.message)
    return result.x


def residual(model,v):
    return float(max(np.abs(model['eq']@v-model['rhs']).max(),
        np.maximum(model['ub']@v-model['b'],0).max(),
        np.maximum(-v,0).max(),np.maximum(v-model['upper'],0).max()))


def repair(model,v):
    n=model['n'];z=np.zeros(n);z[np.argsort(-v[model['z0']:model['o0']],kind='stable')[:model['k']]]=1
    o=np.zeros(n);candidates=np.flatnonzero((z==0)&(v[model['o0']:model['o0']+n]>.5))
    candidates=candidates[np.argsort(-v[model['o0']+candidates],kind='stable')]
    o[candidates[:int(np.floor(model['budget']*n+1e-9))]]=1
    return lp(model,z,o)


def decision(model,v,d):
    n=model['n'];weights=v[:n*n].reshape(n,n).sum(0);support=weights>1e-8
    return optimize(d[support],weights[support]/weights[support].sum(),model['robust'])[0]


def solve(d,k,robust,penalty,budget,flags,variant='partial',epsilon_h=.01,
          epsilon_o=.1,starts=3,maxiter=100,time_limit=10.,seed=0):
    """epsilon_h is Obj1 mass entropy tolerance; z bound is n*epsilon_h.

    partial: continuous deletion. double: binary-entropy deletion.
    continuation: double entropy, gradually reduced tolerances.
    Time limit is cooperative at SLSQP iteration boundaries, not a hard limit.
    """
    if variant not in ('partial','double','continuation'):raise ValueError(variant)
    if epsilon_h<0 or epsilon_o<0:raise ValueError('Entropy tolerances must be nonnegative')
    began=time.perf_counter();m=build(d,k,robust,penalty,budget,flags)
    n=m['n'];zs=slice(m['z0'],m['o0']);os=slice(m['o0'],m['o0']+n)
    rng=np.random.default_rng(seed);relaxed=lp(m);candidates=[];attempts=[];trace=[]
    linear=[LinearConstraint(m['eq'],m['rhs'],m['rhs']),LinearConstraint(m['ub'],-np.inf,m['b'])]
    def check(v,eh,eo):
        return max(residual(m,v),entropy(v[zs])-n*eh,
                   binary_entropy(v[os])-eo if variant!='partial' else 0.)
    # Include LP and LP-refitted hard starts, with diverse random supports.
    initial=[relaxed,repair(m,relaxed)]
    for _ in range(max(starts-2,0)):
        z=np.zeros(n);z[rng.choice(n,k,replace=False)]=1
        initial.append(lp(m,z,np.zeros(n)))
    class Deadline(Exception):pass
    for start in initial[:max(starts,1)]:
        current=start.copy()
        hz=entropy(current[zs]);ho=binary_entropy(current[os])
        schedule=[(epsilon_h,epsilon_o)]
        if variant=='continuation':
            schedule=[(max(epsilon_h,hz/n*f),max(epsilon_o,ho*f)) for f in (1.,.5,.2)]+schedule
        # Retain independently feasible starts even if SLSQP fails later.
        if check(current,epsilon_h,epsilon_o)<=1e-6:candidates.append(current.copy())
        for eh,eo in schedule:
            def hfun(v):
                values=[n*eh-entropy(v[zs])]
                if variant!='partial':values.append(eo-binary_entropy(v[os]))
                return np.array(values)
            def hjac(v):
                jac=np.zeros((1+int(variant!='partial'),len(v)))
                jac[0,zs]=np.log(np.clip(v[zs],1e-12,1))+1
                if variant!='partial':jac[1,os]=np.log(np.clip(v[os],1e-12,1)/np.clip(1-v[os],1e-12,1))
                return jac
            def callback(v):
                if residual(m,v)<1e-6 and np.min(v)>=-1e-10 and np.max(v[zs])<=1+1e-10:
                    safe=np.minimum(np.maximum(v,0),m['upper'])
                    if check(safe,epsilon_h,epsilon_o)<=1e-6:candidates.append(safe.copy())
                if time.perf_counter()-began>time_limit:raise Deadline()
            try:
                result=minimize(lambda v:float(m['c']@v),current,jac=lambda v:m['c'],
                    method='SLSQP',bounds=Bounds(np.zeros(len(current)),m['upper']),
                    constraints=linear+[dict(type='ineq',fun=hfun,jac=hjac)],callback=callback,
                    options=dict(maxiter=maxiter,ftol=1e-8,disp=False))
                current=np.minimum(np.maximum(result.x,0),m['upper'])
                attempts.append(dict(success=bool(result.success),message=str(result.message),iterations=int(result.nit)))
            except Deadline:
                attempts.append(dict(success=False,message='Cooperative time limit',iterations=None));break
            trace.append(dict(epsilon_h=eh,epsilon_o=eo,objective=float(m['c']@current),
                h_z=entropy(current[zs]),h_o=binary_entropy(current[os]),linear_violation=residual(m,current)))
            if check(current,epsilon_h,epsilon_o)<=1e-6:candidates.append(current.copy())
        if time.perf_counter()-began>time_limit:break
    # Always keep a feasible LP-refitted hard support as a labelled fallback.
    fallback=False
    if not candidates:candidates=[repair(m,relaxed)];fallback=True
    best=min(candidates,key=lambda v:float(m['c']@v));fixed=repair(m,best)
    return m,best,fixed,dict(seconds=time.perf_counter()-began,fallback=fallback,
        feasible=bool(check(best,epsilon_h,epsilon_o)<=1e-6),
        entropy_h=entropy(best[zs]),entropy_o=binary_entropy(best[os]),
        h_limit=n*epsilon_h,o_limit=epsilon_o if variant!='partial' else None,
        fractional_z=int(np.sum((best[zs]>1e-6)&(best[zs]<1-1e-6))),
        fractional_o=int(np.sum((best[os]>1e-6)&(best[os]<1-1e-6))),
        linear_violation=residual(m,best),objective=float(m['c']@best),
        repaired_objective=float(m['c']@fixed),attempts=attempts,trace=trace,
        guarantee='Feasible local candidate only; no global optimality certificate')
