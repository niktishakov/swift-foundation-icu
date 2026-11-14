import struct
def read_dat(buf):
    hs = struct.unpack_from('<H', buf, 0)[0]
    n = struct.unpack_from('<I', buf, hs)[0]
    toc = []
    for k in range(n):
        no, do = struct.unpack_from('<II', buf, hs + 4 + 8*k)
        end = buf.index(0, hs + no)
        toc.append([buf[hs+no:end].decode(), hs + do])
    order = sorted(range(n), key=lambda k: toc[k][1])
    for i, k in enumerate(order):
        nxt = toc[order[i+1]][1] if i + 1 < n else len(buf)
        toc[k].append(nxt)
    return hs, toc  # toc in TOC (name) order: [name, start, end]

def write_dat(buf, hs, toc, keep):
    """Rebuild a CmnD file keeping entries whose name satisfies keep(name). Mirrors pkgdata layout."""
    ents = [e for e in toc if keep(e[0])]
    n = len(ents)
    names = b''.join(e[0].encode() + b'\0' for e in ents)
    tocsize = 4 + 8*n
    name_base = tocsize
    data_base = tocsize + len(names)
    data_base = (data_base + 15) & ~15
    out = bytearray(buf[:hs])
    entries = bytearray(struct.pack('<I', n))
    blobs = bytearray()
    noff = name_base
    doff = data_base
    for name, s, e in ents:
        entries += struct.pack('<II', noff, doff)
        noff += len(name.encode()) + 1
        item = buf[s:e]
        blobs += item
        doff += len(item)
    out += entries + names
    out += b'\xaa' * (hs + data_base - len(out))
    out += blobs
    return bytes(out)
