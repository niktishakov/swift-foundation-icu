# ICU data with only some locales

Measurements for the forum topic "Building Foundation with only the locales an app ships". Not a proposal for this repository: the rebuild below is a way to measure, and a maintainable version would use ICU's own `localeFilter` when the data is built from Apple ICU's sources.

## What it does

swift-foundation-icu embeds ICU's data (`icudt76l`, 33,976,096 B) in `icuSources/common/icu_packaged_main_data.{0..3}.inc.h`. The scripts read it back, keep the locale bundles of a list of languages, rebuild the locale trees with `genrb`, and write the data back as `.inc.h` files.

- Kept bundles: every bundle of the chosen languages, plus everything they fall back to: `%%ALIAS` targets, `%%Parent`, ICU's parent table (`localefallback_data.h`) and truncation. `root` always stays. (`select_locales.py`)
- Trees with a shared pool (main, curr, lang, region, unit, zone) are recompiled from text with `genrb`, two passes, with the pool rebuilt from the kept bundles (`rebuild.sh`, `build_variant.sh`). coll, brkitr and rbnf only lose the dropped bundles. Each tree's `res_index` lists only the kept locales (`gen_index.py`).
- Everything that is not locale data stays as it is: supplemental data, time zones, converters, normalization, break rules and dictionaries.
- Check: keeping every locale rebuilds the original data byte for byte.

## Run

Needs Python 3 and `genrb` from ICU 76 or later (`GENRB=/path/to/genrb`, default Homebrew's `icu4c`). From `scripts/`:

```
python3 -I inc_to_dat.py ../../icuSources/common data/icudt76l.dat
python3 -I dat_extract.py data/icudt76l.dat data/items
./emit_trees.sh
python3 -I select_locales.py full en,es,fr,de,it,pt,ru,ja,zh,ar data/variants/top10/keep
./build_variant.sh top10                      # writes data/dats/top10.dat
python3 -I dat_to_inc.py data/dats/top10.dat ../../icuSources/common ../../icuSources/common
```

Then build swift-foundation or swift-corelibs-foundation against this checkout (`SWIFTCI_USE_LOCAL_DEPS`). `probes/` has the tests used to compare outputs; they write a file when `LOCALE_PROBE_OUT` or `ICU_PROBE_OUT` is set.

## Results

Sizes (`results/sizes/`):

| Data | `.dat` | Android app with `import Foundation`, arm64: installed / gzip |
|---|---:|---:|
| all locales | 33,976,096 B | 65,743,029 / 23,956,093 B |
| `top10` (en es fr de it pt ru ja zh ar + regional) | 17,601,056 B | 49,359,029 / 18,906,885 B |
| `en` only | 14,083,024 B | 45,836,469 / 17,498,659 B |

Each language on top of `en`: 148–297 KB, except `zh` 1,783 KB (`per-language.txt`).

Behavior: `results/2026-11-14/tests.md`. The kept locales give the same output as with the full data in swift-foundation (macOS), swift-corelibs-foundation (Linux) and on an Android 16 emulator (`results/2026-10-18-android/`). Dropped locales fall back to the ICU default locale (`en_US_POSIX` style when `LANG` is unset, root otherwise) with no error, and `Locale.availableIdentifiers` lists only the kept locales.
