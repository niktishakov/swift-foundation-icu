# Diff the locale probe (or ICU probe) of a variant against baseline, grouped by locale (first word of each line).
# usage: python3 -I diff_probe.py <baseline.txt> <variant.txt> [--show LOCALE,...]
import sys, collections
a = open(sys.argv[1]).read().split('\n'); b = open(sys.argv[2]).read().split('\n')
show = set(sys.argv[sys.argv.index('--show') + 1].split(',')) if '--show' in sys.argv else set()
assert len(a) == len(b), (len(a), len(b))
same = collections.Counter(); diff = collections.defaultdict(list)
for x, y in zip(a, b):
    k = ' '.join(x.split()[:2]) if x.startswith(('global', 'enc', 'case', 'date', 'num', 'rel', 'list', 'name', 'duration', 'bytes', 'capctx', 'relcap', 'idna')) else x.split()[0]
    if x == y: same[k] += 1
    else: diff[k].append((x, y))
print('identical lines', sum(same.values()), 'different', sum(len(v) for v in diff.values()))
for k, v in diff.items():
    print(f'{k}: {len(v)} differ')
    if k in show or k.split()[-1] in show:
        for x, y in v: print('   -', x); print('   +', y)
