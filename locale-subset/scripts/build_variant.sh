#!/bin/bash
# Build a locale-subset .dat from data/variants/<name>/keep/<tree>.txt (see select_locales.py).
# Pool trees (main, curr, lang, region, unit, zone): kept bundles are re-compiled from .txt with genrb, pool.res
# rebuilt from kept bundles only (rebuild.sh, the same two-pass genrb flow that reproduces the original byte for byte).
# Other trees (coll, brkitr, rbnf): dropped .res items are removed, kept items are unchanged.
# Every tree's res_index.res is regenerated with only kept names (gen_index.py).
# usage: build_variant.sh <name> [input .dat, default data/icudt76l.dat]
set -euo pipefail
cd "$(dirname "$0")"
N=$1; IN=${2:-data/icudt76l.dat}
V=data/variants/$N; I=data/items/icudt76l
G=${GENRB:-/opt/homebrew/opt/icu4c/bin/genrb}
rm -rf $V/build $V/repl; mkdir -p $V/build $V/repl/icudt76l
: > $V/drop.txt
for t in main curr lang region unit zone coll brkitr rbnf; do
  d=$I; p=icudt76l; [ $t != main ] && { d=$I/$t; p=icudt76l/$t; }
  mkdir -p $V/repl/$p
  # dropped bundles
  python3 -I select_names.py $d $V/keep/$t.txt | sed "s#^#$p/#; s#\$#.res#" >> $V/drop.txt
  if [ -d data/txt/$t/pool-src ]; then
    mkdir -p $V/build/$t/txt
    while read -r b; do cp data/txt/$t/pool-src/$b.txt $V/build/$t/txt/; done < $V/keep/$t.txt
    ./rebuild.sh $V/build/$t/txt $V/build/$t/out > $V/build/$t/rebuild.log
    cp $V/build/$t/out/res/*.res $V/repl/$p/
  fi
  python3 -I gen_index.py $d $V/build/$t/idxsrc $V/keep/$t.txt
  $G -q -k -s $V/build/$t/idxsrc -d $V/repl/$p res_index.txt
done
mkdir -p data/dats
python3 -I make_subset_dat.py $IN $V/drop.txt $V/repl data/dats/$N.dat | tee $V/dat.json
