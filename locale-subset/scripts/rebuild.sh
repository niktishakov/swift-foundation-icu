#!/bin/bash
# Rebuild the locale tree .res files (+ pool.res) from derb'd .txt, the way ICU's data build does:
# pass 1 genrb --writePoolBundle over all files, pass 2 genrb --usePoolBundle. Optional filter dir (genrb --filterDir).
# usage: rebuild.sh <txt dir> <out dir> [filter dir]
set -euo pipefail
G=${GENRB:-/opt/homebrew/opt/icu4c/bin/genrb}
TXT=$1; OUT=$2; FILT=${3:-}
rm -rf "$OUT"; mkdir -p "$OUT/pool" "$OUT/res"
FILES=$(cd "$TXT" && ls *.txt)
F=(); [ -n "$FILT" ] && F=(--filterDir "$FILT")
$G -q -k ${F[@]+"${F[@]}"} --writePoolBundle "$OUT/pool" -s "$TXT" -d "$OUT/pool" $FILES > "$OUT/pool.log" 2>&1
$G -q -k ${F[@]+"${F[@]}"} --usePoolBundle "$OUT/pool" -s "$TXT" -d "$OUT/res" $FILES > "$OUT/res.log" 2>&1
cp "$OUT/pool/pool.res" "$OUT/res/pool.res"
if grep -qi error "$OUT/pool.log" "$OUT/res.log"; then echo "genrb errors:"; grep -i error "$OUT/pool.log" "$OUT/res.log" | head; exit 1; fi
echo "files: $(ls "$OUT/res" | wc -l) bytes: $(cat "$OUT"/res/*.res | wc -c)"
