# -*- coding: utf-8 -*-
"""보행노인 / 일반 보행자 사고다발지역 고시목록 대조 분석
데이터: 한국도로교통공단 교통사고정보개방시스템(opendata.koroad.or.kr) 공개 CSV
"""
import csv, math, json, collections, os

BASE = os.path.join(os.path.dirname(__file__), '..', '04-데이터')
OUT  = os.path.join(os.path.dirname(__file__), '..', '04-데이터')
R_MATCH = 150.0   # 두 목록 모두 반경 100m 원 → 중심 간 150m 이내를 동일 지점으로 본다

def load(fn):
    rows = []
    with open(os.path.join(BASE, fn), encoding='cp949', errors='replace') as f:
        for r in csv.DictReader(f):
            try:
                rows.append(dict(
                    yr   = int(str(r['사고다발지id'])[:4]),
                    sgg  = r['시도시군구명'].strip(),
                    nm   = r['지점명'].strip(),
                    occ  = int(r['사고건수']),   cas = int(r['사상자수']),
                    dth  = int(r['사망자수']),   se  = int(r['중상자수']),
                    sl   = int(r['경상자수']),
                    lo   = float(r['경도']),     la  = float(r['위도'])))
            except Exception:
                pass
    return rows

def dist(a, b):
    dy = (a['la'] - b['la']) * 111320.0
    dx = (a['lo'] - b['lo']) * 111320.0 * math.cos(math.radians(a['la']))
    return math.hypot(dx, dy)

def match(A, B, R=R_MATCH):
    """A 의 각 지점에 대해 B 에서 R 이내 최근접을 찾는다. 격자 인덱스로 O(n)."""
    G = collections.defaultdict(list)
    for i, b in enumerate(B):
        G[(round(b['lo'], 2), round(b['la'], 2))].append(i)
    paired, alone = [], []
    for a in A:
        best = None
        for dx in (-0.01, 0.0, 0.01):
            for dy in (-0.01, 0.0, 0.01):
                for i in G[(round(a['lo'], 2) + dx, round(a['la'], 2) + dy)]:
                    d = dist(a, B[i])
                    if d <= R and (best is None or d < best[1]):
                        best = (i, d)
        (paired if best else alone).append((a, best))
    return paired, alone

def lethal(rows):
    """치사율 지표: 사망자수 / 사상자수 (%)"""
    cas = sum(r['cas'] for r in rows); dth = sum(r['dth'] for r in rows)
    return (dth / cas * 100.0) if cas else 0.0

def sido(s):
    return s.split()[0] if s else '미상'

def is_gun(s):
    """비도시 대리지표: 시군구명이 '군' 으로 끝나는 기초자치단체"""
    p = s.split()
    return len(p) > 1 and p[1].rstrip('0123456789').endswith('군')

old = load('12_25_oldman.csv')
ped = load('19_25_pedstrians.csv')
YEARS = [2022, 2023, 2024, 2025, 2026]
result = {'years': {}, 'meta': {'match_radius_m': R_MATCH}}

print('=' * 72)
print('1. 연도별 어긋남 추세 — 노인 다발지역 중 일반 보행자 목록에 없는 지점')
print('=' * 72)
print(f"{'연도':<6}{'노인':>6}{'보행자':>7}{'겹침':>6}{'노인전용':>8}{'비율':>8}"
      f"{'사망':>6}{'중상':>7}{'전용치사율':>10}{'겹침치사율':>10}")
for y in YEARS:
    O = [r for r in old if r['yr'] == y]
    P = [r for r in ped if r['yr'] == y]
    if not O or not P:
        continue
    paired, alone = match(O, P)
    A = [a for a, _ in alone]; C = [a for a, _ in paired]
    row = dict(old=len(O), ped=len(P), overlap=len(C), only=len(A),
               ratio=len(A) / len(O) * 100.0,
               dth=sum(r['dth'] for r in A), se=sum(r['se'] for r in A),
               occ=sum(r['occ'] for r in A),
               leth_only=lethal(A), leth_ov=lethal(C))
    result['years'][y] = row
    print(f"{y:<6}{len(O):>6}{len(P):>7}{len(C):>6}{len(A):>8}{row['ratio']:>7.1f}%"
          f"{row['dth']:>6}{row['se']:>7}{row['leth_only']:>9.2f}%{row['leth_ov']:>9.2f}%")

# ---- 최신 연도 심층 ----
Y = 2026
O = [r for r in old if r['yr'] == Y]; P = [r for r in ped if r['yr'] == Y]
paired, alone = match(O, P)
ONLY = [a for a, _ in alone]; OVER = [a for a, _ in paired]

print()
print('=' * 72)
print(f'2. {Y}년 고시 심층 — 노인 전용 위험지점 {len(ONLY)}곳')
print('=' * 72)
print(f"  사고 {sum(r['occ'] for r in ONLY)}건 · 사상자 {sum(r['cas'] for r in ONLY)}명 · "
      f"사망 {sum(r['dth'] for r in ONLY)}명 · 중상 {sum(r['se'] for r in ONLY)}명")
print(f"  치사율  노인전용 {lethal(ONLY):.2f}%  vs  겹침지점 {lethal(OVER):.2f}%  "
      f"→ {lethal(ONLY)/max(lethal(OVER),1e-9):.2f}배")
print(f"  사망자 발생 지점  노인전용 {sum(1 for r in ONLY if r['dth']>0)}/{len(ONLY)} "
      f"({sum(1 for r in ONLY if r['dth']>0)/len(ONLY)*100:.1f}%)  vs  "
      f"겹침 {sum(1 for r in OVER if r['dth']>0)}/{len(OVER)} "
      f"({sum(1 for r in OVER if r['dth']>0)/len(OVER)*100:.1f}%)")

print()
print('3. 사고건수 분포 — 임계값 격차(5~6건) 구간이 사각지대를 만드는가')
b_only = collections.Counter(min(r['occ'], 10) for r in ONLY)
b_over = collections.Counter(min(r['occ'], 10) for r in OVER)
print(f"  {'사고건수':<10}{'노인전용':>8}{'겹침':>8}")
for k in sorted(set(b_only) | set(b_over)):
    lab = f'{k}건' + ('+' if k == 10 else '')
    print(f"  {lab:<10}{b_only.get(k,0):>8}{b_over.get(k,0):>8}")
gap = sum(v for k, v in b_only.items() if k in (5, 6))
print(f"  → 노인전용 지점의 {gap}/{len(ONLY)}곳({gap/len(ONLY)*100:.1f}%)이 5~6건 구간. "
      f"일반 기준 임계 7건에 못 미쳐 구조적으로 목록에 오르지 못한다.")

print()
print('4. 도시 / 비도시 — 「이동의 격차」 축')
gu_only = [r for r in ONLY if is_gun(r['sgg'])]; gu_all = [r for r in O if is_gun(r['sgg'])]
si_only = [r for r in ONLY if not is_gun(r['sgg'])]; si_all = [r for r in O if not is_gun(r['sgg'])]
print(f"  군 지역   노인다발 {len(gu_all):>4}곳 중 전용 {len(gu_only):>3}곳 "
      f"({len(gu_only)/max(len(gu_all),1)*100:.1f}%)  치사율 {lethal(gu_only):.2f}%")
print(f"  시·구 지역 노인다발 {len(si_all):>4}곳 중 전용 {len(si_only):>3}곳 "
      f"({len(si_only)/max(len(si_all),1)*100:.1f}%)  치사율 {lethal(si_only):.2f}%")

print()
print('5. 시도별 노인 전용 위험지점')
cnt = collections.Counter(sido(r['sgg']) for r in ONLY)
tot = collections.Counter(sido(r['sgg']) for r in O)
print(f"  {'시도':<12}{'전용':>5}{'노인다발':>8}{'비율':>8}{'사망':>6}")
sido_rows = []
for k, v in cnt.most_common():
    d = sum(r['dth'] for r in ONLY if sido(r['sgg']) == k)
    print(f"  {k:<12}{v:>5}{tot[k]:>8}{v/tot[k]*100:>7.1f}%{d:>6}")
    sido_rows.append(dict(sido=k, only=v, total=tot[k], ratio=v/tot[k]*100, dth=d))
result['sido'] = sido_rows

print()
print('6. 사망자 발생 노인 전용 위험지점 (정책 최우선 대상)')
top = sorted([r for r in ONLY if r['dth'] > 0],
             key=lambda r: (-r['dth'], -r['se']))
for r in top[:15]:
    print(f"  {r['sgg']:<14} {r['nm'][:38]:<40} 사고{r['occ']:>2} 사망{r['dth']} 중상{r['se']:>2}")
result['top'] = [dict(sgg=r['sgg'], nm=r['nm'], occ=r['occ'], dth=r['dth'],
                      se=r['se'], lo=r['lo'], la=r['la']) for r in top]

# ---- 역방향 ----
paired_r, alone_r = match(P, O)
REV = [a for a, _ in alone_r]
print()
print('7. 역방향 — 일반 보행자 다발이나 노인 목록에 없는 지점')
print(f"  {len(REV)}곳 / {len(P)}곳 ({len(REV)/len(P)*100:.1f}%)  치사율 {lethal(REV):.2f}%")
result['reverse'] = dict(n=len(REV), total=len(P), leth=lethal(REV))

# ---- 산출물 ----
result['only_points'] = [dict(sgg=r['sgg'], nm=r['nm'], occ=r['occ'], cas=r['cas'],
                              dth=r['dth'], se=r['se'], lo=r['lo'], la=r['la'])
                         for r in ONLY]
result['over_points'] = [dict(sgg=r['sgg'], nm=r['nm'], occ=r['occ'], cas=r['cas'],
                              dth=r['dth'], se=r['se'], lo=r['lo'], la=r['la'])
                         for r in OVER]
result['bins'] = dict(only=dict(b_only), over=dict(b_over))
result['urban'] = dict(gun=dict(total=len(gu_all), only=len(gu_only), leth=lethal(gu_only)),
                       si=dict(total=len(si_all), only=len(si_only), leth=lethal(si_only)))
result['summary'] = dict(year=Y, only=len(ONLY), over=len(OVER), old=len(O), ped=len(P),
                         dth=sum(r['dth'] for r in ONLY), se=sum(r['se'] for r in ONLY),
                         occ=sum(r['occ'] for r in ONLY),
                         leth_only=lethal(ONLY), leth_over=lethal(OVER))
with open(os.path.join(OUT, 'result.json'), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)
print('\n→ 04-데이터/result.json 저장')
