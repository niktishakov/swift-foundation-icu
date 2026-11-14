# Test runs, 14 Nov 2026: full data vs `top10`

`top10` = en, es, fr, de, it, pt, ru, ja, zh, ar and their regional locales (17,601,056 B of 33,976,096 B).

| Run | Full data | `top10` |
|---|---|---|
| swift-foundation d53ce9c, macOS 27, Swift 6.4, `swift test` | 45 + 570 + 1755 tests pass | 58 issues in 12 tests, every one in a dropped locale |
| swift-corelibs-foundation 06fda2d (with the same swift-foundation), Linux aarch64, `swift:6.4.1-noble`, `swift test --parallel` | 1935 tests pass | 2 tests fail, both use a dropped locale |

swift-foundation, failing tests with `top10` (locale in parentheses):

- `DatePatternFormattingTests`: `names` (cs, sv), `localizedGMTForms` (fi, am, …), `localizedGMTWithSeconds` (fi, fa), `negativeYearMinusSign` (sv, fi, …), `defaultDigits` (ne, fa, mr, hi@numbers=native), `localeDigits` (ff_Adlm), `noon` (pl, tr), `identifierForms` (sr_Latn), `scriptFallback` (az_RU, sr_Latn_XX), `capitalization` (cs, ca)
- `ListFormatStyleTests.contextualHebrew` (he)
- `NumberFormatStyleTests.floatingPointFormatStyle_BigNumber` (uz_Cyrl)

swift-corelibs-foundation, failing tests with `top10`:

- `TestDateFormatter.test_orderOfPropertySetters` (nb)
- `TestNSLocale.test_staticProperties` (expects `gl_ES` in `Locale.availableIdentifiers`)

Probes (`../../probes`, output in `macos/` and `linux/`, with `LANG` unset and `LANG=de_DE.UTF-8`): every line for the 21 kept locales is identical to the full data. Lines that change: the dropped locales (ko_KR, tr_TR, he_IL, nl_NL, pl_PL, sv_SE, hi_IN, th_TH, uk_UA, yue) and the global counts (`Locale.availableIdentifiers` 1034 → 316). corelibs string encodings, transliteration and word-boundary regex are unchanged.
