# Write a .dat as the 4 icu_packaged_main_data.N.inc.h chunks in ICUExport's format (same writer as ../../scripts/trim.py).
# usage: python3 -I dat_to_inc.py <in.dat> <original icu common dir> <out dir>
import sys, re, os
dat, src, dst = sys.argv[1:4]
out = open(dat, 'rb').read()
assert len(out) % 4 == 0
os.makedirs(dst, exist_ok=True)
chunk = len(out) // 4
for i in range(4):
    orig = open(f'{src}/icu_packaged_main_data.{i}.inc.h').read()
    m = re.search(r'#define __ICU_PACKAGED_MAIN_DATA_CHUNK_%d ' % i, orig)
    prefix = orig[:m.end()]
    suffix = orig[orig.rfind('0x') + 4:]
    part = out[i * chunk:(i + 1) * chunk]
    lines = [', '.join('0x%02X' % b for b in part[j:j + 32]) for j in range(0, len(part), 32)]
    open(f'{dst}/icu_packaged_main_data.{i}.inc.h', 'w').write(prefix + ', \\\n    '.join(lines) + suffix)
print('wrote', dst, len(out))
