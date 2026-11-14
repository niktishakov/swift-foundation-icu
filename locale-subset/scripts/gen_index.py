# Write res_index.txt for one tree, keeping only the given bundle names (all if no keep file).
# Key order matches ICU's generated res_index.txt (CLDRVersion, InstalledLocales, AliasLocales), so an unfiltered
# run rebuilds the original byte for byte.
# usage: python3 -I gen_index.py <orig tree dir> <out txt dir> [keep file]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icu_res
d, out = sys.argv[1:3]
keep = set(open(sys.argv[3]).read().split()) if len(sys.argv) > 3 else None
t = icu_res.load(d, 'res_index')
os.makedirs(out, exist_ok=True)
L = ['﻿res_index:table(nofallback){\n']
if 'CLDRVersion' in t: L.append('    CLDRVersion{"%s"}\n' % t['CLDRVersion'])
for k in ('InstalledLocales', 'AliasLocales'):
    if k not in t: continue
    L.append('    %s:table{\n' % k)
    for n in t[k]:
        if keep is None or n in keep: L.append('        %s{""}\n' % n)
    L.append('    }\n')
L.append('}\n')
open(os.path.join(out, 'res_index.txt'), 'w', encoding='utf-8').write(''.join(L))
