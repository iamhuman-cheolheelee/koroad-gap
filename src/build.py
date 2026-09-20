# -*- coding: utf-8 -*-
"""데모 단일 HTML 빌드 — data.json 을 인라인해 외부 의존을 지도 타일로만 한정한다"""
import json, os
d = os.path.dirname(os.path.abspath(__file__))
data = open(os.path.join(d, 'data.json'), encoding='utf-8').read()
tpl  = open(os.path.join(d, 'index.tpl.html'), encoding='utf-8').read()
sido = open(os.path.join(d, 'sido.json'), encoding='utf-8').read()
out  = tpl.replace('/*__DATA__*/null', data).replace('/*__SIDO__*/null', sido)
open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html', os.path.getsize(os.path.join(d,'index.html')), 'bytes')
