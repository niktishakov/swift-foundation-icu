#!/bin/bash
# Emit genrb .txt sources for every pool-using bundle of each pool tree, and for every tree's res_index.
# Output: data/txt/<tree>/*.txt (tree "main" = icudt76l/ itself), data/txt/<tree>/lists/{pool,index}.txt
# usage: emit_trees.sh
set -euo pipefail
cd "$(dirname "$0")"
I=data/items/icudt76l
for t in main curr lang region unit zone coll brkitr rbnf; do
  d=$I; [ $t != main ] && d=$I/$t
  mkdir -p data/txt/$t/lists
  python3 -I - "$d" > data/txt/$t/lists/pool.txt <<'PY'
import sys, os
sys.path.insert(0, '.')
import icu_res
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if f.endswith('.res'):
        b = icu_res.Bundle(open(os.path.join(d, f), 'rb').read())
        if b.usesPool: print(f[:-4])
PY
  echo res_index > data/txt/$t/lists/index.txt
  [ -s data/txt/$t/lists/pool.txt ] && python3 -I emit_txt.py $d data/txt/$t/lists/pool.txt data/txt/$t/pool-src
  python3 -I emit_txt.py $d data/txt/$t/lists/index.txt data/txt/$t/index-src
done
