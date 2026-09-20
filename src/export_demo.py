# -*- coding: utf-8 -*-
"""데모 웹앱용 연도별 3분류 지점 데이터 추출"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from analyze import load, match, lethal, is_gun, sido   # noqa

old = load('12_25_oldman.csv'); ped = load('19_25_pedstrians.csv')
out = {}
for y in (2022, 2023, 2024, 2025, 2026):
    O = [r for r in old if r['yr'] == y]; P = [r for r in ped if r['yr'] == y]
    if not O or not P: continue
    pa, al = match(O, P)
    only = [a for a, _ in al]; over = [a for a, _ in pa]
    pa2, al2 = match(P, O)
    rev = [a for a, _ in al2]
    def pk(rows, kind):
        return [[round(r['lo'],5), round(r['la'],5), r['occ'], r['dth'], r['se'],
                 r['sgg'], r['nm'], kind] for r in rows]
    out[y] = dict(
        pts = pk(only,0) + pk(over,1) + pk(rev,2),
        stat = dict(old=len(O), ped=len(P), only=len(only), over=len(over), rev=len(rev),
                    dth=sum(r['dth'] for r in only), se=sum(r['se'] for r in only),
                    occ=sum(r['occ'] for r in only),
                    leth_only=round(lethal(only),2), leth_over=round(lethal(over),2),
                    leth_rev=round(lethal(rev),2)),
        bins = {str(k): [sum(1 for r in only if min(r['occ'],10)==k),
                         sum(1 for r in over if min(r['occ'],10)==k)] for k in range(3,11)})
p = os.path.join(os.path.dirname(__file__), '..', '06-데모', 'data.json')
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(out, open(p,'w',encoding='utf-8'), ensure_ascii=False, separators=(',',':'))
print('저장:', p, os.path.getsize(p), 'bytes')
for y,v in out.items(): print(y, v['stat'])
