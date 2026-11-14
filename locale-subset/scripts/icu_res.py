# Minimal reader for ICU binary resource bundles (.res, formatVersion 2/3), little-endian.
# Library module; also CLI: python3 -I icu_res.py <resdir> <bundle> [path/in/bundle]
import struct, sys, os, json

class Bundle:
    def __init__(self, data, pool=None):
        hs = struct.unpack_from('<H', data, 0)[0]
        self.fmt = data[16]
        self.d = data[hs:]
        d = self.d
        self.root = struct.unpack_from('<I', d, 0)[0]
        idx0 = struct.unpack_from('<I', d, 4)[0]
        ilen = idx0 & 0xff
        self.idx = struct.unpack_from('<%dI' % ilen, d, 4)
        keysTop = self.idx[1]
        self.localKeyLimit = 0
        if keysTop > 1 + ilen:
            self.localKeyLimit = keysTop << 2
        self.poolStrLimit = 0
        self.poolStr16Limit = 0
        if self.fmt >= 3:
            self.poolStrLimit = idx0 >> 8
        att = self.idx[5] if ilen > 5 else 0
        self.usesPool = bool(att & 4)
        self.isPool = bool(att & 2)
        self.noFallback = bool(att & 1)
        self.poolStrLimit |= (att & 0xf000) << 12
        self.poolStr16Limit = att >> 16
        self.p16 = keysTop * 4 if (ilen > 6 and self.idx[6] > keysTop) else None
        self.pool = pool
        self.poolKeysOff = 4 * (1 + ilen)

    def u16(self, off):  # off in 16-bit units relative to p16
        return struct.unpack_from('<H', self.d, self.p16 + 2 * off)[0]

    def key(self, off, is32=False):
        if is32:
            if off & 0x80000000:
                return self.pool._cstr(self.pool.poolKeysOff + (off & 0x7fffffff))
            return self._cstr(off)
        if off < self.localKeyLimit:
            return self._cstr(off)
        return self.pool._cstr(self.pool.poolKeysOff + off - self.localKeyLimit)

    def _cstr(self, off):
        e = self.d.index(b'\0', off)
        return self.d[off:e].decode('ascii')

    def str16(self, src, off):  # STRING_V2 decoding from bundle src's p16 at off
        first = src.u16(off)
        if not (0xdc00 <= first <= 0xdfff):
            n = 0
            while src.u16(off + n) != 0:
                n += 1
            start = off
        elif first < 0xdfef:
            n = first & 0x3ff; start = off + 1
        elif first < 0xdfff:
            n = ((first - 0xdfef) << 16) | src.u16(off + 1); start = off + 2
        else:
            n = (src.u16(off + 1) << 16) | src.u16(off + 2); start = off + 3
        b = src.d[src.p16 + 2 * start: src.p16 + 2 * (start + n)]
        return b.decode('utf-16-le', 'surrogatepass')

    def res(self, r):
        t = r >> 28; o = r & 0x0fffffff; d = self.d
        if t == 6:  # STRING_V2
            if o < self.poolStrLimit:
                return self.str16(self.pool, o)
            return self.str16(self, o - self.poolStrLimit)
        if t in (0, 3):  # STRING / ALIAS
            if o == 0:
                s = ''
            else:
                n = struct.unpack_from('<i', d, 4 * o)[0]
                s = d[4 * o + 4: 4 * o + 4 + 2 * n].decode('utf-16-le', 'surrogatepass')
            return ('ALIAS', s) if t == 3 else s
        if t == 7:  # INT (28-bit signed)
            return o - (1 << 28) if o & 0x08000000 else o
        if t == 1:
            return ('BINARY', o)
        if t == 14:
            n = struct.unpack_from('<i', d, 4 * o)[0]
            return list(struct.unpack_from('<%di' % n, d, 4 * o + 4))
        if t == 2:  # TABLE
            if o == 0: return {}
            n = struct.unpack_from('<H', d, 4 * o)[0]
            keys = struct.unpack_from('<%dH' % n, d, 4 * o + 2)
            base = 4 * o + 2 + 2 * n + (2 if (n & 1) == 0 else 0)
            items = struct.unpack_from('<%dI' % n, d, base)
            return {self.key(k): self.res(v) for k, v in zip(keys, items)}
        if t == 5:  # TABLE16
            n = self.u16(o)
            keys = [self.u16(o + 1 + i) for i in range(n)]
            items = [self.u16(o + 1 + n + i) for i in range(n)]
            return {self.key(k): self.res(self.from16(v)) for k, v in zip(keys, items)}
        if t == 4:  # TABLE32
            n = struct.unpack_from('<i', d, 4 * o)[0]
            keys = struct.unpack_from('<%dI' % n, d, 4 * o + 4)
            items = struct.unpack_from('<%dI' % n, d, 4 * o + 4 + 4 * n)
            return {self.key(k, True): self.res(v) for k, v in zip(keys, items)}
        if t == 8:  # ARRAY
            if o == 0: return []
            n = struct.unpack_from('<i', d, 4 * o)[0]
            items = struct.unpack_from('<%dI' % n, d, 4 * o + 4)
            return [self.res(v) for v in items]
        if t == 9:  # ARRAY16
            n = self.u16(o)
            return [self.res(self.from16(self.u16(o + 1 + i))) for i in range(n)]
        raise ValueError('type %d' % t)

    def from16(self, r16):
        if r16 >= self.poolStr16Limit:
            r16 = r16 - self.poolStr16Limit + self.poolStrLimit
        return (6 << 28) | r16

    def top(self):
        return self.res(self.root)

_pools = {}
def load(resdir, name):
    if resdir not in _pools:
        p = os.path.join(resdir, 'pool.res')
        _pools[resdir] = Bundle(open(p, 'rb').read()) if os.path.exists(p) else None
    path = os.path.join(resdir, name + '.res')
    if not os.path.exists(path):
        return None
    return Bundle(open(path, 'rb').read(), _pools[resdir]).top()

if __name__ == '__main__':
    t = load(sys.argv[1], sys.argv[2])
    for k in (sys.argv[3].split('/') if len(sys.argv) > 3 else []):
        t = t[k]
    print(json.dumps(t, ensure_ascii=False, indent=1, default=str)[:20000])
