# Per-tree item bytes (as stored in the .dat, padding included) for several .dat files.
# usage: python3 -I tree_sizes.py <a.dat> <b.dat> ...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datlib import read_dat
def tree(name):
    p = name.split('/')
    if len(p) == 2: return 'converters (*.cnv)' if p[1].endswith('.cnv') else ('main tree *.res' if p[1].endswith('.res') else 'other top-level')
    return p[1]
cols = []
for f in sys.argv[1:]:
    buf = open(f, 'rb').read(); hs, toc = read_dat(buf)
    c = collections.Counter(); n = collections.Counter()
    for name, s, e in toc: c[tree(name)] += e - s; n[tree(name)] += 1
    c['TOC + header'] = len(buf) - sum(c.values()); c['TOTAL .dat'] = len(buf)
    cols.append((os.path.basename(f)[:-4], c, n))
keys = sorted(cols[0][1], key=lambda k: (k in ('TOC + header', 'TOTAL .dat'), -cols[0][1][k]))
print('| tree | ' + ' | '.join(c[0] for c in cols) + ' |')
print('|---|' + '---:|' * len(cols))
for k in keys:
    row = [f'{cols[0][1][k]:,}']
    for name, c, n in cols[1:]:
        row.append(f'{c[k]:,} ({c[k] - cols[0][1][k]:+,})')
    print(f'| {k} | ' + ' | '.join(row) + ' |')
