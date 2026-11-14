// Temporary probe for locale-subset ICU data: dumps locale-dependent outputs, one locale per block, so a run with a
// subset .dat can be diffed against baseline. Output file: $LOCALE_PROBE_OUT.
import Testing

#if canImport(FoundationEssentials)
@testable import FoundationEssentials
@testable import FoundationInternationalization
#else
@testable import Foundation
#endif

@Suite struct LocaleSubsetProbeTests {
    @Test func dumpLocaleOutputs() throws {
        var lines: [String] = []
        func log(_ s: String) { lines.append(s) }
        let ids = Set(Locale.availableIdentifiers)
        log("global availableIdentifiers=\(ids.count) ko=\(ids.contains("ko")) ko_KR=\(ids.contains("ko_KR")) en_US=\(ids.contains("en_US")) en_GB=\(ids.contains("en_GB")) zh_Hant_HK=\(ids.contains("zh_Hant_HK")) yue=\(ids.contains("yue"))")
        log("global availableCollations=\(Locale.Collation.availableCollations.count) commonISOCurrencyCodes=\(Locale.commonISOCurrencyCodes.count) knownTimeZones=\(TimeZone.knownTimeZoneIdentifiers.count) isoLanguages=\(Locale.LanguageCode.isoLanguageCodes.count) isoRegions=\(Locale.Region.isoRegions.count)")
        log("global current=\(Locale.current.identifier) \(Date(timeIntervalSince1970: 1_800_000_000).formatted(Date.FormatStyle(date: .complete, time: .omitted, locale: .current, timeZone: .gmt)))")
        let date = Date(timeIntervalSince1970: 1_800_000_000)
        let ny = TimeZone(identifier: "America/New_York")!
        let locales = ["en_US", "en_GB", "en_IN", "en_US_POSIX", "es_ES", "es_MX", "es_419", "fr_FR", "fr_CA", "de_DE", "de_CH", "it_IT",
                       "pt_BR", "pt_PT", "ru_RU", "ja_JP", "zh_Hans_CN", "zh_Hant_TW", "zh_Hant_HK", "ar_EG", "ar_SA",
                       "ko_KR", "tr_TR", "he_IL", "nl_NL", "pl_PL", "sv_SE", "hi_IN", "th_TH", "uk_UA", "yue", "xx_YY"]
        for l in locales {
            let loc = Locale(identifier: l)
            log("\(l) date \(date.formatted(Date.FormatStyle(date: .complete, time: .complete, locale: loc, timeZone: .gmt))) | \(date.formatted(Date.FormatStyle(date: .numeric, time: .shortened, locale: loc, timeZone: .gmt))) | \(date.formatted(Date.FormatStyle(locale: loc, timeZone: .gmt).month(.wide).weekday(.abbreviated)))")
            log("\(l) num \(1234567.891.formatted(.number.locale(loc))) | \(0.42.formatted(.percent.locale(loc))) | \(99.5.formatted(.currency(code: "EUR").locale(loc))) | \(1234.5.formatted(.currency(code: loc.currency?.identifier ?? "USD").locale(loc))) | \(12345.formatted(.number.notation(.compactName).locale(loc))) | \(1e-7.formatted(.number.notation(.scientific).locale(loc)))")
            log("\(l) props currency=\(loc.currency?.identifier ?? "nil") dec=\(loc.decimalSeparator ?? "nil") grp=\(loc.groupingSeparator ?? "nil") numsys=\(loc.numberingSystem.identifier) measure=\(loc.measurementSystem.identifier) firstDay=\(loc.firstDayOfWeek) hourCycle=\(loc.hourCycle) cal=\(loc.calendar.identifier) quote=\(loc.quotationBeginDelimiter ?? "nil")")
            log("\(l) list \(["a", "b", "c"].formatted(.list(type: .and).locale(loc))) | \(["a", "b"].formatted(.list(type: .or).locale(loc)))")
            log("\(l) rel \(Date.now.addingTimeInterval(-3 * 86400 - 60).formatted(Date.RelativeFormatStyle(presentation: .named, unitsStyle: .wide).locale(loc))) | \(Date.now.addingTimeInterval(2 * 3600 + 60).formatted(Date.RelativeFormatStyle(presentation: .numeric, unitsStyle: .abbreviated).locale(loc)))")
            log("\(l) dur \(Duration.seconds(3725).formatted(.units(allowed: [.hours, .minutes, .seconds], width: .wide).locale(loc))) | \(Duration.seconds(3725).formatted(.time(pattern: .hourMinuteSecond).locale(loc))) | \(Int64(1_234_567).formatted(.byteCount(style: .file).locale(loc)))")
            log("\(l) names lang(de)=\(loc.localizedString(forLanguageCode: "de") ?? "nil") region(JP)=\(loc.localizedString(forRegionCode: "JP") ?? "nil") cur(EUR)=\(loc.localizedString(forCurrencyCode: "EUR") ?? "nil") script(Cyrl)=\(loc.localizedString(forScriptCode: "Cyrl") ?? "nil") id(fr_CA)=\(loc.localizedString(forIdentifier: "fr_CA") ?? "nil") tz=\(ny.localizedName(for: .generic, locale: loc) ?? "nil")/\(ny.localizedName(for: .shortStandard, locale: loc) ?? "nil")")
            var cal = Calendar(identifier: .gregorian); cal.locale = loc
            log("\(l) cal months=\(cal.monthSymbols.prefix(2)) wd=\(cal.shortWeekdaySymbols.prefix(2)) firstWeekday=\(cal.firstWeekday) minDays=\(cal.minimumDaysInFirstWeek) am=\(cal.amSymbol)")
            log("\(l) case \("istanbul iı".uppercased(with: loc)) | \("hello world ǆ".capitalized(with: loc)) | collations=\(Locale.Collation.availableCollations(for: loc.language).map(\.identifier))")
        }
        guard let path = ProcessInfo.processInfo.environment["LOCALE_PROBE_OUT"] else { return }
        try lines.joined(separator: "\n").write(toFile: path, atomically: true, encoding: .utf8)
        print("locale probe wrote \(lines.count) lines to \(path)")
    }
}
