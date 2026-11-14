# Write a CmnD .dat: drop the items named in <drop file> and replace items with files from <repl dir>
# (laid out by item name, e.g. <repl>/icudt76l/curr/pool.res). Same pkgdata layout as make_dat.py
# (TOC, names, each item padded to 16 bytes with 0xaa). Replacing an item that is not in the .dat is an error.
# usage: python3 -I make_subset_dat.py <in.dat> <drop file> <repl dir> <out.dat>
import sys, os, struct, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datlib import read_dat
src, dropf, repld, outp = sys.argv[1:5]
buf = open(src, 'rb').read()
hs, toc = read_dat(buf)
drop = set(open(dropf).read().split())
repl = {}
for dp, _, fs in os.walk(repld):
    for f in fs:
        p = os.path.join(dp, f); repl[os.path.relpath(p, repld)] = open(p, 'rb').read()
names = {e[0] for e in toc}
assert drop <= names, sorted(drop - names)[:5]
assert set(repl) <= names, sorted(set(repl) - names)[:5]
assert not (drop & set(repl))
def tree(name):
    p = name.split('/')
    if len(p) == 2: return 'cnv' if p[1].endswith('.cnv') else ('main .res' if p[1].endswith('.res') else 'main other')
    return p[1]
delta = collections.Counter()
ents = [e for e in toc if e[0] not in drop]
n = len(ents)
nameblob = b''.join(e[0].encode() + b'\0' for e in ents)
data_base = (4 + 8 * n + len(nameblob) + 15) & ~15
out = bytearray(buf[:hs]); entries = bytearray(struct.pack('<I', n)); blobs = bytearray()
noff, doff = 4 + 8 * n, data_base
for name, s, e in toc:
    if name in drop:
        delta[tree(name)] -= e - s; continue
    entries += struct.pack('<II', noff, doff)
    noff += len(name.encode()) + 1
    item = buf[s:e]
    if name in repl:
        item = repl[name] + b'\xaa' * (((len(repl[name]) + 15) & ~15) - len(repl[name]))
        delta[tree(name)] += len(item) - (e - s)
    blobs += item; doff += len(item)
out += entries + nameblob
out += b'\xaa' * (hs + data_base - len(out))
out += blobs
open(outp, 'wb').write(out)
items_delta = sum(delta.values())
print(json.dumps(dict(items_in=len(toc), items_out=n, dropped=len(drop), replaced=len(repl), size_in=len(buf),
    size_out=len(out), delta=len(out) - len(buf), delta_items=items_delta, delta_toc=len(out) - len(buf) - items_delta,
    delta_by_tree=dict(sorted(delta.items()))), indent=1))
