# -*- coding: utf-8 -*-
"""보고서 삽입용 벡터 그림 생성 — 인쇄 해상도를 위해 래스터 대신 SVG 로 직접 생성한다"""
import json, os, math

d    = os.path.dirname(os.path.abspath(__file__))
FIG  = os.path.join(d, '..', 'figures')
os.makedirs(FIG, exist_ok=True)
R    = json.load(open(os.path.join(d, '..', 'data', 'result.json'), encoding='utf-8'))
SIDO = json.load(open(os.path.join(d, '..', 'src', 'sido.json'), encoding='utf-8'))

ONLY, OVER = '#C2410C', '#94A3B8'
INK, INK2, INK3, LINE = '#111827', '#374151', '#6B7280', '#E5E7EB'
F = 'font-family="Pretendard, Apple SD Gothic Neo, Noto Sans KR, sans-serif"'

def save(name, body, w, h):
    p = os.path.join(FIG, name)
    open(p, 'w', encoding='utf-8').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>')
    print('·', name)

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ── 그림 1. 전국 지도 ──────────────────────────────────────────────
def fig_map():
    W, H = 640, 820
    lo0, lo1, la0, la1 = 125.9, 129.7, 33.0, 38.7
    MAPH = 742
    sx = W / (lo1 - lo0); sy = MAPH / (la1 - la0)
    s = min(sx, sy) * 0.97
    ox = (W - (lo1 - lo0) * s) / 2; oy = (MAPH - (la1 - la0) * s) / 2
    X = lambda lo: ox + (lo - lo0) * s
    Y = lambda la: MAPH - oy - (la - la0) * s
    out = []
    for f in SIDO['features']:
        for poly in f['geometry']['coordinates']:
            pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in poly[0])
            out.append(f'<polygon points="{pts}" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="0.7"/>')
    for p in R['over_points']:
        out.append(f'<circle cx="{X(p["lo"]):.1f}" cy="{Y(p["la"]):.1f}" '
                   f'r="{2.4+min(p["occ"],12)*0.24:.1f}" fill="{OVER}" fill-opacity="0.45"/>')
    for p in R['only_points']:
        r = 3.0 + min(p['occ'], 12) * 0.3
        out.append(f'<circle cx="{X(p["lo"]):.1f}" cy="{Y(p["la"]):.1f}" r="{r:.1f}" '
                   f'fill="{ONLY}" fill-opacity="0.9" stroke="#fff" '
                   f'stroke-width="{1.4 if p["dth"]>0 else 0.7}"/>')
    ly = H - 18
    out.append(f'<circle cx="24" cy="{ly}" r="5" fill="{ONLY}"/>'
               f'<text x="35" y="{ly+4}" {F} font-size="12" fill="{INK2}">'
               f'노인 목록에만 있는 지점 {R["summary"]["only"]}곳</text>')
    out.append(f'<circle cx="300" cy="{ly}" r="4" fill="{OVER}" fill-opacity="0.6"/>'
               f'<text x="311" y="{ly+4}" {F} font-size="12" fill="{INK3}">'
               f'양쪽 목록에 모두 있는 지점 {R["summary"]["over"]}곳</text>')
    save('fig1-map.svg', ''.join(out), W, H)

# ── 그림 2. 임계값 분포 ────────────────────────────────────────────
def fig_bins():
    W, H = 760, 380
    b = R['bins']; keys = sorted(int(k) for k in set(b['only']) | set(b['over']))
    mx = max(max(b['only'].get(str(k), b['only'].get(k, 0)) for k in keys),
             max(b['over'].get(str(k), b['over'].get(k, 0)) for k in keys))
    g = lambda dd, k: dd.get(str(k), dd.get(k, 0))
    X0, Y0, PW, PH = 58, 296, 660, 236
    bw = PW / len(keys)
    out = []
    i7 = keys.index(7) if 7 in keys else None
    if i7 is not None:
        out.append(f'<rect x="{X0+i7*bw-3:.1f}" y="30" width="{PW-i7*bw+3:.1f}" '
                   f'height="{Y0-30}" fill="#F3F4F6"/>')
        out.append(f'<text x="{X0+i7*bw+8:.1f}" y="48" {F} font-size="12.5" '
                   f'font-weight="700" fill="{INK3}">일반 기준 임계값 7건 이상 구간</text>')
    for i, k in enumerate(keys):
        x = X0 + i * bw
        for j, (v, col) in enumerate(((g(b['only'], k), ONLY), (g(b['over'], k), OVER))):
            h = v / mx * PH if mx else 0
            if h > 0:
                out.append(f'<rect x="{x+5+j*(bw/2-4):.1f}" y="{Y0-h:.1f}" '
                           f'width="{bw/2-9:.1f}" height="{h:.1f}" fill="{col}" rx="3"/>')
            if v:
                out.append(f'<text x="{x+5+j*(bw/2-4)+(bw/2-9)/2:.1f}" y="{Y0-h-7:.1f}" '
                           f'text-anchor="middle" {F} font-size="12" font-weight="700" '
                           f'fill="{INK2}">{v}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{Y0+20}" text-anchor="middle" {F} '
                   f'font-size="12.5" fill="{INK3}">{"10건+" if k==10 else str(k)+"건"}</text>')
    out.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0+PW}" y2="{Y0}" stroke="#D1D5DB"/>')
    out.append(f'<text x="0" y="20" {F} font-size="14" font-weight="700" fill="{INK}">'
               f'사고건수 구간별 지점 수 (2026년 고시)</text>')
    for i, (t, c) in enumerate((('노인 목록에만 있음', ONLY), ('양쪽 목록에 모두 있음', OVER))):
        out.append(f'<rect x="{X0+i*210}" y="{Y0+44}" width="11" height="11" fill="{c}" rx="2"/>'
                   f'<text x="{X0+i*210+17}" y="{Y0+54}" {F} font-size="12.5" fill="{INK2}">{t}</text>')
    save('fig2-threshold.svg', ''.join(out), W, H)

# ── 그림 3. 연도별 추세 ────────────────────────────────────────────
def fig_trend():
    W, H = 760, 340
    ys = sorted(R['years']); vals = [R['years'][y]['ratio'] for y in ys]
    X0, Y0, PW, PH = 58, 258, 660, 200
    mx = 40
    px = lambda i: X0 + i * PW / (len(ys) - 1)
    py = lambda v: Y0 - v / mx * PH
    out = []
    for gl in range(0, mx + 1, 10):
        out.append(f'<line x1="{X0}" y1="{py(gl):.1f}" x2="{X0+PW}" y2="{py(gl):.1f}" stroke="#F3F4F6"/>'
                   f'<text x="{X0-10}" y="{py(gl)+4:.1f}" text-anchor="end" {F} '
                   f'font-size="11.5" fill="#9CA3AF">{gl}%</text>')
    out.append('<polyline points="' + ' '.join(f'{px(i):.1f},{py(v):.1f}' for i, v in enumerate(vals))
               + f'" fill="none" stroke="{ONLY}" stroke-width="2.4" stroke-linejoin="round"/>')
    for i, (y, v) in enumerate(zip(ys, vals)):
        out.append(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="5.5" fill="{ONLY}" '
                   f'stroke="#fff" stroke-width="2"/>'
                   f'<text x="{px(i):.1f}" y="{py(v)-15:.1f}" text-anchor="middle" {F} '
                   f'font-size="12.5" font-weight="700" fill="{ONLY}">{v:.1f}%</text>'
                   f'<text x="{px(i):.1f}" y="{Y0+20}" text-anchor="middle" {F} '
                   f'font-size="12.5" fill="{INK3}">{y}년</text>')
    out.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0+PW}" y2="{Y0}" stroke="#D1D5DB"/>')
    out.append(f'<text x="0" y="20" {F} font-size="14" font-weight="700" fill="{INK}">'
               f'노인 다발지역 중 일반 목록에 오르지 못한 지점의 비율</text>')
    save('fig3-trend.svg', ''.join(out), W, H)

# ── 그림 4. 분석 파이프라인 ────────────────────────────────────────
def fig_pipe():
    W, H = 760, 250
    steps = [('① 수집', '두 고시 목록\n공개 데이터셋 2종'),
             ('② 전처리', '연도 분리 · 좌표 정규화\nEPSG 4326'),
             ('③ 공간 대조', '격자 인덱스 기반\n최근접 매칭 150m'),
             ('④ 분류', '노인 전용 / 겹침\n/ 일반 전용'),
             ('⑤ 해석', '임계값 구간 분포\n· 추세 · 지역 분포')]
    bw, gap = 128, 22
    x0 = (W - (bw * len(steps) + gap * (len(steps) - 1))) / 2
    out = [f'<text x="0" y="20" {F} font-size="14" font-weight="700" fill="{INK}">'
           f'분석 파이프라인</text>']
    for i, (t, sub) in enumerate(steps):
        x = x0 + i * (bw + gap)
        out.append(f'<rect x="{x:.1f}" y="60" width="{bw}" height="104" rx="9" '
                   f'fill="#FFF" stroke="{ONLY if i==2 else LINE}" '
                   f'stroke-width="{1.8 if i==2 else 1}"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="88" text-anchor="middle" {F} font-size="13" '
                   f'font-weight="700" fill="{ONLY if i==2 else INK}">{t}</text>')
        for j, ln in enumerate(sub.split('\n')):
            out.append(f'<text x="{x+bw/2:.1f}" y="{112+j*17}" text-anchor="middle" {F} '
                       f'font-size="11" fill="{INK3}">{esc(ln)}</text>')
        if i < len(steps) - 1:
            ax = x + bw + 4
            out.append(f'<path d="M{ax} 112 L{ax+gap-8} 112" stroke="#9CA3AF" stroke-width="1.4" '
                       f'marker-end="url(#a)"/>')
    out.append('<defs><marker id="a" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" '
               'markerHeight="6" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="#9CA3AF"/>'
               '</marker></defs>')
    out.append(f'<text x="{x0:.1f}" y="196" {F} font-size="11.5" fill="{INK3}">'
               f'전 과정이 결정적(deterministic)이다. 난수·학습 파라미터가 없으므로 같은 입력에 '
               f'항상 같은 결과가 나온다.</text>')
    save('fig4-pipeline.svg', ''.join(out), W, H)

fig_map(); fig_bins(); fig_trend(); fig_pipe()
print('완료')
