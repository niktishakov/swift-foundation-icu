// Temporary probe: dumps outputs of ICU-backed APIs so runs with different ICU data can be diffed.
import Testing

#if canImport(FoundationEssentials)
@testable import FoundationEssentials
@testable import FoundationInternationalization
#else
@testable import Foundation
#endif

@Suite struct ICUDataProbeTests {
    @Test func dumpICUBackedOutputs() throws {
        var lines: [String] = []
        func log(_ s: String) { lines.append(s) }

        // 1. String encodings handled by ICU converters
        let samples = ["Hello, world", "Grüße — café", "日本語のテキスト", "Привет, мир", "Γειά σου", "Çok güzel", "Žluťoučký kůň", "©®™ “quotes” …"]
        let encodings: [String.Encoding] = [.japaneseEUC, .isoLatin1, .shiftJIS, .isoLatin2, .windowsCP1250, .windowsCP1251, .windowsCP1252, .windowsCP1253, .windowsCP1254, .iso2022JP, .macOSRoman]
        for enc in encodings {
            for s in samples {
                let strict = s.data(using: enc, allowLossyConversion: false)
                let lossy = s.data(using: enc, allowLossyConversion: true)
                let back = lossy.flatMap { String(data: $0, encoding: enc) }
                log("enc \(enc.rawValue) \(s) strict=\(strict?.count ?? -1) lossy=\(lossy.map { Array($0) } ?? []) back=\(back ?? "nil")")
            }
        }

        // 2. Case mapping incl. title case (uses word break iterator)
        let caseSamples = ["hello world. new sentence", "ǆemal ijssel", "истанбул и ı i", "this is 中文和english混合 text", "ภาษาไทย test word", "ខ្មែរ word test", "ພາສາລາວ word", "မြန်မာ word", "日本語 と english words", "o'neil mcdonald-smith"]
        let locales = ["en_US", "tr_TR", "nl_NL", "lt_LT", "el_GR", "ja_JP", "zh_CN", "th_TH"]
        for l in locales {
            let loc = Locale(identifier: l)
            for s in caseSamples {
                log("case \(l) \(s) | up=\(s.uppercased(with: loc)) | low=\(s.lowercased(with: loc)) | title=\(s.capitalized(with: loc))")
            }
        }

        // 3. Collation: ICU compare is only compiled with FOUNDATION_ICU_STRING_COMPARE (off in package builds).

        // 4. Formatting
        let date = Date(timeIntervalSince1970: 1_800_000_000)
        for l in ["en_US", "de_DE", "ja_JP", "th_TH", "ar_SA", "zh_Hant_TW", "km_KH", "my_MM"] {
            let loc = Locale(identifier: l)
            log("date \(l) \(date.formatted(.dateTime.locale(loc))) | \(date.formatted(.dateTime.weekday(.wide).month(.wide).day().year().locale(loc)))")
            log("num \(l) \(1234567.891.formatted(.number.locale(loc))) | \(0.42.formatted(.percent.locale(loc))) | \(99.5.formatted(.currency(code: "EUR").locale(loc)))")
            log("rel \(l) \(date.formatted(.relative(presentation: .named).locale(loc)))")
            log("list \(l) \(["a", "b", "c"].formatted(.list(type: .and).locale(loc)))")
            log("name \(l) \(loc.localizedString(forLanguageCode: "fr") ?? "nil") \(loc.localizedString(forRegionCode: "BR") ?? "nil")")
        }

        // 4b. Unit-backed formatting and capitalization contexts (unit data, break iterators)
        for l in ["en_US", "de_DE", "fr_FR", "es_ES", "ru_RU", "ja_JP", "ar_EG"] {
            let loc = Locale(identifier: l)
            log("duration \(l) \(Duration.seconds(3725).formatted(.units(allowed: [.hours, .minutes, .seconds], width: .wide).locale(loc))) | \(Duration.seconds(3725).formatted(.time(pattern: .hourMinuteSecond).locale(loc)))")
            log("bytes \(l) \(Int64(1_234_567).formatted(.byteCount(style: .file).locale(loc)))")
            var fs = Date.FormatStyle(date: .complete, time: .omitted, locale: loc, timeZone: .gmt)
            fs.capitalizationContext = .beginningOfSentence
            var fl = Date.FormatStyle(date: .complete, time: .omitted, locale: loc, timeZone: .gmt)
            fl.capitalizationContext = .listItem
            log("capctx \(l) \(Date(timeIntervalSince1970: 1_800_000_000).formatted(fs)) | \(Date(timeIntervalSince1970: 1_800_000_000).formatted(fl))")
            log("rel \(l) \(Date(timeIntervalSince1970: 1_800_000_000).formatted(Date.RelativeFormatStyle(presentation: .named).locale(loc)))")
            if ProcessInfo.processInfo.environment["ICU_PROBE_RELCAP"] != nil {
                log("relcap \(l) \(Date(timeIntervalSince1970: 1_800_000_000).formatted(Date.RelativeFormatStyle(presentation: .named, capitalizationContext: .beginningOfSentence).locale(loc)))")
            }
        }

        // 5. IDNA
        for host in ["bücher.example", "例え.テスト", "xn--bcher-kva.example", "ПРИМЕР.рф"] {
            let url = URL(string: "https://\(host)/path")
            log("idna \(host) \(url?.host(percentEncoded: true) ?? "nil")")
        }

        guard let path = ProcessInfo.processInfo.environment["ICU_PROBE_OUT"] else { return }
        try lines.joined(separator: "\n").write(toFile: path, atomically: true, encoding: .utf8)
        print("ICU probe wrote \(lines.count) lines to \(path)")
    }
}
