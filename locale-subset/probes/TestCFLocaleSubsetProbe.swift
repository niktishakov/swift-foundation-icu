// Temporary probe, not for the repository: dumps CoreFoundation's locale-dependent outputs (NSLocale, DateFormatter, NumberFormatter, collation) for kept and dropped locales, so runs with different ICU data can be diffed.

class TestCFLocaleSubsetProbe: XCTestCase {
    func test_dumpLocaleOutputs() throws {
        guard let path = ProcessInfo.processInfo.environment["LOCALE_PROBE_OUT"] else { return }
        var lines: [String] = []
        func log(_ s: String) { lines.append(s) }

        let ids = Locale.availableIdentifiers
        log("global availableIdentifiers=\(ids.count) NSLocale=\(NSLocale.availableLocaleIdentifiers.count) ko=\(ids.contains("ko")) en_GB=\(ids.contains("en_GB")) zh_Hant_HK=\(ids.contains("zh_Hant_HK"))")
        log("global isoCurrencies=\(NSLocale.isoCurrencyCodes.count) isoLanguages=\(NSLocale.isoLanguageCodes.count) isoCountries=\(NSLocale.isoCountryCodes.count)")

        let locales = ["en_US", "en_GB", "en_IN", "en_US_POSIX", "es_ES", "es_MX", "es_419", "fr_FR", "fr_CA", "de_DE", "de_CH", "it_IT",
                       "pt_BR", "pt_PT", "ru_RU", "ja_JP", "zh_Hans_CN", "zh_Hant_TW", "zh_Hant_HK", "ar_EG", "ar_SA",
                       "ko_KR", "tr_TR", "he_IL", "nl_NL", "pl_PL", "sv_SE", "hi_IN", "th_TH", "uk_UA", "yue", "xx_YY"]
        let date = Date(timeIntervalSince1970: 1_800_000_000)
        let words = ["Äpfel", "apple", "Zebra", "zebra", "ähnlich", "Ångström", "ch", "cz", "čaj", "ıi", "Iİ", "日本", "中国", "한국", "ไทย", "file10", "file2"]
        for l in locales {
            let loc = Locale(identifier: l)
            let ns = NSLocale(localeIdentifier: l)
            log("\(l) props dec=\(loc.decimalSeparator ?? "nil") grp=\(loc.groupingSeparator ?? "nil") cur=\(loc.currency?.identifier ?? "nil")/\(loc.currencySymbol ?? "nil") quote=\(loc.quotationBeginDelimiter ?? "nil")\(loc.quotationEndDelimiter ?? "nil") firstWeekday=\(loc.calendar.firstWeekday)")
            log("\(l) names lang(de)=\(ns.displayName(forKey: .languageCode, value: "de") ?? "nil") region(JP)=\(ns.displayName(forKey: .countryCode, value: "JP") ?? "nil") cur(EUR)=\(ns.displayName(forKey: .currencyCode, value: "EUR") ?? "nil") id(fr_CA)=\(ns.displayName(forKey: .identifier, value: "fr_CA") ?? "nil")")
            let df = DateFormatter(); df.locale = loc; df.timeZone = TimeZone(identifier: "UTC")
            for (d, t) in [(DateFormatter.Style.full, DateFormatter.Style.long), (.medium, .short), (.short, .none)] {
                df.dateStyle = d; df.timeStyle = t
                log("\(l) date \(d.rawValue)/\(t.rawValue) \(df.string(from: date))")
            }
            df.setLocalizedDateFormatFromTemplate("yMMMMd jm")
            log("\(l) template \(df.dateFormat ?? "nil") \(df.string(from: date)) months=\(df.monthSymbols.prefix(2)) weekdays=\(df.shortWeekdaySymbols.prefix(2))")
            let nf = NumberFormatter(); nf.locale = loc
            for style in [NumberFormatter.Style.decimal, .currency, .percent, .scientific, .spellOut, .ordinal] {
                nf.numberStyle = style
                log("\(l) num \(style.rawValue) \(nf.string(from: 1234567.891) ?? "nil")")
            }
            log("\(l) sort \(words.sorted { $0.compare($1, options: [], range: nil, locale: loc) == .orderedAscending })")
            log("\(l) sortCI \(words.sorted { $0.compare($1, options: [.caseInsensitive, .diacriticInsensitive], range: nil, locale: loc) == .orderedAscending })")
            log("\(l) case up=\("istanbul ılık straße".uppercased(with: loc)) low=\("İSTANBUL IŞIK".lowercased(with: loc)) cap=\("istanbul ijssel".capitalized(with: loc))")
        }

        try lines.joined(separator: "\n").write(toFile: path, atomically: true, encoding: .utf8)
        print("locale probe wrote \(lines.count) lines to \(path)")
    }
}
