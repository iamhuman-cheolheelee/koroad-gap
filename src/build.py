# -*- coding: utf-8 -*-
"""데모 단일 HTML 빌드: data.json·시도 경계·Leaflet·기관 로고·검증값을 모두 인라인해 외부 요청 0"""
import json, os, base64
d = os.path.dirname(os.path.abspath(__file__))
r = lambda *p: open(os.path.join(d, *p), encoding='utf-8').read()
b64 = lambda p: 'data:image/png;base64,' + base64.b64encode(open(os.path.join(d, p), 'rb').read()).decode()
sens = json.load(open(os.path.join(d, '..', 'data', 'sensitivity.json'), encoding='utf-8'))
out = (r('index.tpl.html')
       .replace('/*__LEAFLET_JS__*/', r('vendor', 'leaflet.js'))
       .replace('/*__LEAFLET_CSS__*/', r('vendor', 'leaflet.css'))
       .replace('/*__DATA__*/null', r('data.json'))
       .replace('/*__SIDO__*/null', r('sido.json'))
       .replace('/*__SENS__*/null', json.dumps({'radius': sens['radius']}, separators=(',', ':')))
       .replace('/*__LOGO_SHE__*/', b64('assets/숲과나눔_로고.png'))
       .replace('/*__LOGO_HANI__*/', b64('assets/한겨레_로고.png')))
open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html', os.path.getsize(os.path.join(d, 'index.html')), 'bytes')
