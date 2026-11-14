# Compare two locale-tree .res directories: sizes (raw and padded to 16 bytes as in the .dat) and decoded content.
# usage: python3 -I compare.py <dirA> <dirB> [--drop path,...]   (--drop: paths expected to be missing in B)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icu_res

def pad16(n):
    return (n + 15) & ~15

def drop(tree, path):
    ks = path.split('/')
    t = tree
    for k in ks[:-1]:
        if not isinstance(t, dict) or k not in t:
            return
        t = t[k]
    if isinstance(t, dict):
        t.pop(ks[-1], None)

def prune_empty(t):
    if isinstance(t, dict):
        for k in list(t):
            prune_empty(t[k])
            if t[k] == {}:
                del t[k]

a, b = sys.argv[1], sys.argv[2]
drops = sys.argv[sys.argv.index('--drop') + 1].split(',') if '--drop' in sys.argv else []
names = sorted(f[:-4] for f in os.listdir(a) if f.endswith('.res'))
sa = sb = pa = pb = 0
diff = []
missing = []
for n in names:
    fa = os.path.join(a, n + '.res'); fb = os.path.join(b, n + '.res')
    if not os.path.exists(fb):
        missing.append(n); continue
    za, zb = os.path.getsize(fa), os.path.getsize(fb)
    sa += za; sb += zb; pa += pad16(za); pb += pad16(zb)
    if n == 'pool':
        continue
    ta, tb = icu_res.load(a, n), icu_res.load(b, n)
    for p in drops:
        drop(ta, p)
    prune_empty(ta); prune_empty(tb)
    if json.dumps(ta, sort_keys=True, default=str) != json.dumps(tb, sort_keys=True, default=str):
        diff.append(n)
print(json.dumps(dict(files=len(names), missing=missing, bytes_a=sa, bytes_b=sb, delta=sb - sa,
                      padded16_a=pa, padded16_b=pb, padded16_delta=pb - pa,
                      content_diff_count=len(diff), content_diff=diff[:20]), indent=1))
