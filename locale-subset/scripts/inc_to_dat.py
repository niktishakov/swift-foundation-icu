# Read the ICU data that swift-foundation-icu embeds (icu_packaged_main_data.{0..3}.inc.h) back into one .dat file.
# usage: python3 -I inc_to_dat.py <icuSources/common dir> <out.dat>
import re, sys
src, out = sys.argv[1:3]
data = b''
for i in range(4):
    text = open(f'{src}/icu_packaged_main_data.{i}.inc.h').read()
    start = re.search(r'#define __ICU_PACKAGED_MAIN_DATA_CHUNK_%d ' % i, text).end()
    data += bytes(int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{2})\b', text[start:]))
import os
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
open(out, 'wb').write(data)
print('wrote', out, len(data))
