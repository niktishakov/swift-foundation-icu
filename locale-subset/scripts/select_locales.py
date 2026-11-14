# Choose the locale bundles to keep in every locale-keyed tree.
# mode "full": every bundle whose language subtag is in LANGS (en -> en, en_GB, en_US_POSIX, ...);
# mode "base": only the bundles named exactly in LANGS.
# Then, per tree, closure over: %%ALIAS target, %%Parent, ICU's compiled-in parent table (localefallback_data.h) and
# truncation parents; alias-only bundles whose target is kept are kept too (they are listed in res_index AliasLocales).
# root is always kept; non-locale bundles (supplementalData, pool, res_index, ...) are not touched by this script.
# usage: python3 -I select_locales.py <full|base> <lang,lang,...> <out dir>
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icu_res
mode, langs, out = sys.argv[1], set(sys.argv[2].split(',')), sys.argv[3]
I = 'data/items/icudt76l'
TREES = ['main', 'coll', 'brkitr', 'rbnf', 'curr', 'lang', 'region', 'unit', 'zone']
ICU = os.environ.get('ICU_SOURCES', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'icuSources'))
PT = dict(re.findall(r'//\s*(\S+) -> (\S+)', open(ICU + '/common/localefallback_data.h').read().split('parentLocaleTable[]')[1]))

def locale_bundles(d):
    r = []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.res') or f in ('pool.res', 'res_index.res'): continue
        b = icu_res.Bundle(open(os.path.join(d, f), 'rb').read())
        # in pool trees only pool users are locale bundles; plain ones are supplementalData, tzdbNames, metaZones, ...
        if os.path.exists(os.path.join(d, 'pool.res')) and not b.usesPool: continue
        r.append(f[:-4])
    return r

os.makedirs(out, exist_ok=True)
summary = []
for t in TREES:
    d = I if t == 'main' else I + '/' + t
    names = locale_bundles(d)
    S = set(names)
    top = {n: icu_res.load(d, n) for n in names}
    def links(n):
        v = top[n]; r = []
        if isinstance(v, dict):
            for k in ('%%ALIAS', '%%Parent'):
                if k in v: r.append(v[k])
        if n in PT: r.append(PT[n])
        if '_' in n: r.append(n.rsplit('_', 1)[0])
        return [x for x in r if x in S]
    if mode == 'full': keep = {n for n in names if n.split('_')[0] in langs}
    else: keep = {n for n in names if n in langs}
    keep.add('root')
    while True:
        add = {x for n in keep for x in links(n)} - keep
        add |= {n for n in names if isinstance(top[n], dict) and top[n].get('%%ALIAS') in keep} - keep
        if not add: break
        keep |= add
    extra = sorted(n for n in keep if n.split('_')[0] not in langs and n != 'root')
    open(os.path.join(out, t + '.txt'), 'w').write('\n'.join(sorted(keep)) + '\n')
    summary.append('%-6s bundles %4d kept %4d dropped %4d  kept-from-other-langs: %s' % (t, len(names), len(keep), len(names) - len(keep), ','.join(extra)))
print('\n'.join(summary))
