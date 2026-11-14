# Write ICU .res bundles back as genrb .txt sources (replacement for derb, which truncates strings that contain '"'
# and does not escape '\'). Typed decoder based on ../listformat-diff/notes/icu_res.py.
# usage: python3 -I emit_txt.py <resdir> <bundle list file> <out txt dir>
import sys, os, struct, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icu_res

class T(icu_res.Bundle):
    def tres(self, r):
        t = r >> 28; o = r & 0x0fffffff; d = self.d
        if t == 6:
            return ('str', self.res(r))
        if t in (0, 3):
            v = self.res(r)
            return ('alias', v[1]) if t == 3 else ('str', v)
        if t == 7:
            return ('int', self.res(r))
        if t == 1:
            n = struct.unpack_from('<i', d, 4 * o)[0] if o else 0
            return ('bin', d[4 * o + 4: 4 * o + 4 + n] if o else b'')
        if t == 14:
            return ('intv', self.res(r) if o else [])
        if t == 2:
            if o == 0: return ('table', [])
            n = struct.unpack_from('<H', d, 4 * o)[0]
            keys = struct.unpack_from('<%dH' % n, d, 4 * o + 2)
            base = 4 * o + 2 + 2 * n + (2 if (n & 1) == 0 else 0)
            items = struct.unpack_from('<%dI' % n, d, base)
            return ('table', [(self.key(k), self.tres(v)) for k, v in zip(keys, items)])
        if t == 5:
            n = self.u16(o)
            keys = [self.u16(o + 1 + i) for i in range(n)]
            items = [self.u16(o + 1 + n + i) for i in range(n)]
            return ('table', [(self.key(k), self.tres(self.from16(v))) for k, v in zip(keys, items)])
        if t == 4:
            n = struct.unpack_from('<i', d, 4 * o)[0]
            keys = struct.unpack_from('<%dI' % n, d, 4 * o + 4)
            items = struct.unpack_from('<%dI' % n, d, 4 * o + 4 + 4 * n)
            return ('table', [(self.key(k, True), self.tres(v)) for k, v in zip(keys, items)])
        if t == 8:
            if o == 0: return ('array', [])
            n = struct.unpack_from('<i', d, 4 * o)[0]
            items = struct.unpack_from('<%dI' % n, d, 4 * o + 4)
            return ('array', [self.tres(v) for v in items])
        if t == 9:
            n = self.u16(o)
            return ('array', [self.tres(self.from16(self.u16(o + 1 + i))) for i in range(n)])
        raise ValueError(t)

def q(s):
    out = []
    b = s.encode('utf-16-le', 'surrogatepass')
    units = struct.unpack('<%dH' % (len(b) // 2), b)
    i = 0
    while i < len(units):
        u = units[i]
        if 0xd800 <= u <= 0xdbff and i + 1 < len(units) and 0xdc00 <= units[i + 1] <= 0xdfff:
            out.append(chr(0x10000 + ((u - 0xd800) << 10) + (units[i + 1] - 0xdc00))); i += 2; continue
        c = chr(u)
        if c == '\\': out.append('\\\\')
        elif c == '"': out.append('\\"')
        elif u < 0x20 or 0x7f <= u <= 0x9f or 0xd800 <= u <= 0xdfff: out.append('\\u%04X' % u)
        else: out.append(c)
        i += 1
    return '"' + ''.join(out) + '"'

def emit(node, ind, w):
    k, v = node
    p = '    ' * ind
    if k == 'str': w(q(v))
    elif k == 'alias': w(q(v))
    elif k == 'int': w(str(v))
    elif k == 'intv': w(', '.join(str(x) for x in v))
    elif k == 'bin': w('"' + v.hex() + '"')
    elif k == 'table':
        w('\n')
        for key, item in v:
            w(p + '    ' + q(key) + TYPE[item[0]] + '{')
            emit(item, ind + 1, w)
            w('}\n' if item[0] not in ('table', 'array') else p + '    }\n')
        return
    elif k == 'array':
        w('\n')
        for item in v:
            w(p + '    ' + TYPE[item[0]] + '{')
            emit(item, ind + 1, w)
            w('},\n' if item[0] not in ('table', 'array') else p + '    },\n')
        return

TYPE = {'str': '', 'alias': ':alias', 'int': ':int', 'intv': ':intvector', 'bin': ':bin', 'table': ':table', 'array': ':array'}

if __name__ == '__main__':
    resdir, lst, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    pp = os.path.join(resdir, "pool.res"); pool = icu_res.Bundle(open(pp, "rb").read()) if os.path.exists(pp) else None
    for name in open(lst).read().split():
        b = T(open(os.path.join(resdir, name + '.res'), 'rb').read(), pool)
        top = b.tres(b.root)
        parts = []
        attr = ':table(nofallback)' if b.noFallback else ''
        parts.append('﻿' + name + attr + '{')
        emit(top, 0, parts.append)
        parts.append('}\n')
        open(os.path.join(out, name + '.txt'), 'w', encoding='utf-8').write(''.join(parts))
    print('written', len(open(lst).read().split()))
