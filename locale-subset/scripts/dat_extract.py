# Extract items from an ICU common data (.dat, CmnD) file.
# usage: python3 -I dat_extract.py <in.dat> <outdir> [name-substring-filter ...]
import sys, struct, os
dat, outdir, filt = sys.argv[1], sys.argv[2], sys.argv[3:]
b = open(dat, 'rb').read()
hs = struct.unpack_from('<H', b, 0)[0]
toc = hs
n = struct.unpack_from('<I', b, toc)[0]
ents = []
for i in range(n):
    no, do = struct.unpack_from('<II', b, toc + 4 + 8 * i)
    name = b[toc + no: b.index(b'\0', toc + no)].decode()
    ents.append((name, toc + do))
ends = [e[1] for e in ents[1:]] + [len(b)]
cnt = 0
for (name, off), end in zip(ents, ends):
    if filt and not any(f in name for f in filt):
        continue
    p = os.path.join(outdir, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(b[off:end]); cnt += 1
print('items', n, 'extracted', cnt, 'first', ents[0][0])
