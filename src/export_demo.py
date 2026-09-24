# -*- coding: utf-8 -*-
"""데모 웹앱용 연도별 원자료 추출 (v2, 2026-09-25)
O = 보행노인 다발지역 전체, P = 보행자 다발지역 전체. 좌표는 원값 그대로 둔다.
데모가 브라우저에서 반경별 매칭을 다시 계산하므로 반올림하면 경계 지점이 바뀔 수 있다.
stat·bins 는 150m 기준 검산용으로 함께 넣는다.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from analyze import load, match, lethal   # noqa

old = load('12_25_oldman.csv'); ped = load('19_25_pedstrians.csv')
out = {}
row = lambda r: [r['lo'], r['la'], r['occ'], r['dth'], r['se'], r['sgg'], r['nm'], r['cas']]
for y in (2022, 2023, 2024, 2025, 2026):
    O = [r for r in old if r['yr'] == y]; P = [r for r in ped if r['yr'] == y]
    if not O or not P: continue
    pa, al = match(O, P)
    only = [a for a, _ in al]; over = [a for a, _ in pa]
    rev = [a for a, _ in match(P, O)[1]]
    out[y] = dict(
        O=[row(r) for r in O], P=[row(r) for r in P],
        stat=dict(old=len(O), ped=len(P), only=len(only), over=len(over), rev=len(rev),
                  dth=sum(r['dth'] for r in only), se=sum(r['se'] for r in only),
                  occ=sum(r['occ'] for r in only),
                  leth_only=round(lethal(only), 2), leth_over=round(lethal(over), 2),
                  leth_rev=round(lethal(rev), 2)),
        bins={str(k): [sum(1 for r in only if min(r['occ'], 10) == k),
                       sum(1 for r in over if min(r['occ'], 10) == k)] for k in range(3, 11)})
p = os.path.join(os.path.dirname(__file__), '..', 'src', 'data.json')
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('저장:', p, os.path.getsize(p), 'bytes')
for y, v in out.items(): print(y, v['stat'])
