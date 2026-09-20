# -*- coding: utf-8 -*-
"""시도 경계 GeoJSON 을 Douglas-Peucker 로 간소화해 데모에 내장한다.
외부 지도 타일에 의존하지 않기 위함 — 심사 환경에서 네트워크가 막혀도 지도가 그려진다."""
import json, math, os

TOL = 0.004          # 약 400m. 전국 축척에서는 육안 차이가 없다
MIN_AREA = 0.0009    # 아주 작은 부속 도서는 뺀다

def perp(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    if dx == 0 and dy == 0: return math.hypot(p[0]-a[0], p[1]-a[1])
    t = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / (dx*dx+dy*dy)))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))

def dp(pts, tol):
    if len(pts) < 3: return pts
    dmax, idx = 0, 0
    for i in range(1, len(pts)-1):
        d = perp(pts[i], pts[0], pts[-1])
        if d > dmax: dmax, idx = d, i
    if dmax > tol:
        return dp(pts[:idx+1], tol)[:-1] + dp(pts[idx:], tol)
    return [pts[0], pts[-1]]

def area(ring):
    s = 0
    for i in range(len(ring)-1):
        s += ring[i][0]*ring[i+1][1] - ring[i+1][0]*ring[i][1]
    return abs(s)/2

src = json.load(open('/tmp/sido.json', encoding='utf-8'))
feats = []
for f in src['features']:
    g = f['geometry']
    polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    keep = []
    for poly in polys:
        ring = poly[0]
        if area(ring) < MIN_AREA: continue
        r = dp([[round(x,4), round(y,4)] for x, y in ring], TOL)
        if len(r) > 3: keep.append([r])
    if keep:
        feats.append({'type':'Feature','properties':{},
                      'geometry':{'type':'MultiPolygon','coordinates':keep}})
out = {'type':'FeatureCollection','features':feats}
p = os.path.join(os.path.dirname(__file__), '..', '06-데모', 'sido.json')
json.dump(out, open(p,'w',encoding='utf-8'), separators=(',',':'))
print('시도', len(feats), '·', os.path.getsize(p), 'bytes')
