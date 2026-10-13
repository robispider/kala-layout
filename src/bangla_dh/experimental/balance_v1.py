"""Experimental Balance v1 with frozen calibration, outside official scoring."""
from __future__ import annotations
from fractions import Fraction
import math


def cost(values, aspirations, scales, weights, rho):
    if not (len(values)==len(aspirations)==len(scales)==len(weights)==4):
        raise ValueError('Balance v1 requires four components')
    if any(not math.isfinite(v) for v in [*values,*aspirations,*scales,*weights,rho]):
        raise ValueError('finite components and parameters required')
    if any(t<=0 for t in scales) or any(w<=0 for w in weights) or rho<=0:
        raise ValueError('positive scales, weights and augmentation required')
    terms=[w*(x-a)/t for x,a,t,w in zip(values,aspirations,scales,weights)]
    return (max(terms)+rho*sum(terms))/sum(weights)


def credit_deficit(lower,upper):
    if not 0<=lower<=upper<=1: raise ValueError('invalid credit bounds')
    return 1-upper,1-lower


def eligibility(metrics,reference):
    effort=Fraction(metrics['J1_exact'])<=Fraction(reference['J1_exact'])*Fraction(201,200)
    within=metrics['within_distance']<=reference['within_distance']*1.05+1e-14
    return effort and within,effort,within


def evaluate(metrics,calibration):
    """Return one R, evaluated only against the supplied frozen constants.

    No candidate pool is accepted: adding a candidate cannot refit b_minus.
    Ineligible maps have no eligible score or rank.
    """
    allowed,effort,within=eligibility(metrics,calibration['reference'])
    if not allowed:
        return {'eligible':False,'effort_cap_pass':effort,'within_cap_pass':within,'R':None,'worst_setting':None}
    deficit_lower,deficit_upper=credit_deficit(metrics['order_lower'],metrics['order_upper'])
    values=[metrics['J1'],metrics['cross_distance'],metrics['within_distance'],deficit_upper]
    scores=[]
    for setting in calibration['settings']:
        b=cost(values,calibration['aspirations'],calibration['scales'],setting['weights'],setting['rho'])
        scores.append((max(0.,b-setting['b_minus']),setting['id'],b,setting['b_minus']))
    if len(scores)!=81: raise ValueError('Balance v1 requires exactly 81 frozen settings')
    worst=max(scores,key=lambda v:(v[0],v[1]))
    return {'eligible':True,'effort_cap_pass':effort,'within_cap_pass':within,'R':worst[0],
        'worst_setting':worst[1],'worst_B_plus':worst[2],'worst_b_minus':worst[3]}
