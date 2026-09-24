# -*- coding: utf-8 -*-
"""검증 스크립트 — analyze.py 결과의 강건성 확인
1) 격자 인덱스 매칭 = 전수 비교 매칭 인지 (연도별 노인 전용 지점 집합 비교)
2) 매칭 반경 민감도 (100/150/200/300m)
3) 역방향 지점 1:1 강제(보행자 지점 재사용 금지) 시 결과 변화
산출: data/sensitivity.json
"""
import os, json, math, contextlib, io
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'analyze.py'), encoding='utf-8').read()
cut = src.index("old = load(")
ns = {'__file__': os.path.join(here, 'analyze.py')}
exec(src[:cut], ns)
load, dist, match = ns['load'], ns['dist'], ns['match']
old = load('12_25_oldman.csv'); ped = load('19_25_pedstrians.csv')
YEARS = [2022, 2023, 2024, 2025, 2026]

def brute(A, B, R):
    return [a for a in A if not any(dist(a, b) <= R for b in B)]

def strict11(A, B, R):
    pairs = sorted((dist(a, b), i, j) for i, a in enumerate(A) for j, b in enumerate(B) if dist(a, b) <= R)
    ua, ub = set(), set()
    for d, i, j in pairs:
        if i not in ua and j not in ub: ua.add(i); ub.add(j)
    return [a for i, a in enumerate(A) if i not in ua]

key = lambda r: (r['nm'], r['lo'], r['la'])
out = {'grid_vs_brute': {}, 'radius': {}, 'strict_1to1': {}}
for y in YEARS:
    O = [r for r in old if r['yr'] == y]; P = [r for r in ped if r['yr'] == y]
    g = {key(a) for a, _ in match(O, P)[1]}
    b = {key(a) for a in brute(O, P, 150.0)}
    out['grid_vs_brute'][y] = dict(grid=len(g), brute=len(b), identical=(g == b))
    out['radius'][y] = {int(R): len(brute(O, P, R)) for R in (100.0, 150.0, 200.0, 300.0)}
    s = strict11(O, P, 150.0)
    out['strict_1to1'][y] = dict(only=len(s), bins_5_6=sum(1 for a in s if a['occ'] in (5, 6)))
    # 반경별 5~6건 비중 (2026 핵심 주장 강건성)
    out.setdefault('radius_bins56', {})[y] = {int(R): (lambda L: [len(L), sum(1 for a in L if a['occ'] in (5, 6))])(brute(O, P, R)) for R in (100.0, 200.0, 300.0)}
json.dump(out, open(os.path.join(here, '..', 'data', 'sensitivity.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
