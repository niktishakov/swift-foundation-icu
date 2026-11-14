# Print the locale bundles of a tree directory that are NOT in the keep file (same definition of "locale bundle"
# as select_locales.py). usage: python3 -I select_names.py <tree dir> <keep file>
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icu_res
d, keepf = sys.argv[1:3]
keep = set(open(keepf).read().split())
pool = os.path.exists(os.path.join(d, 'pool.res'))
for f in sorted(os.listdir(d)):
    if not f.endswith('.res') or f in ('pool.res', 'res_index.res'): continue
    if pool and not icu_res.Bundle(open(os.path.join(d, f), 'rb').read()).usesPool: continue
    if f[:-4] not in keep: print(f[:-4])
