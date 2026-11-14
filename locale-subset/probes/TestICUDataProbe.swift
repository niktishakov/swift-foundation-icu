// Temporary probe for swift-corelibs-foundation: dumps outputs of ICU-backed CoreFoundation APIs
// (encodings, transforms, regex word boundaries, collation, formatting) so runs with different ICU data can be diffed.

class TestICUDataProbe: XCTestCase {
    func test_dumpICUBackedOutputs() throws {
        guard let path = ProcessInfo.processInfo.environment["ICU_PROBE_OUT"] else { return }
        var lines: [String] = []
        func log(_ s: String) { lines.append(s) }

        // 1. Every encoding CoreFoundation reports as available
        let samples = ["Hello, world", "Grüße — café", "日本語のテキスト", "中文简体", "繁體中文", "한국어", "Привет, мир", "Γειά σου", "שלום", "مرحبا", "ภาษาไทย", "Žluťoučký kůň"]
        let available = String.availableStringEncodings.sorted { $0.rawValue < $1.rawValue }
        log("available \(available.count): \(available.map { $0.rawValue })")
        for enc in available {
            var parts: [String] = []
            for s in samples {
                let strict = s.data(using: enc, allowLossyConversion: false)
                let lossy = s.data(using: enc, allowLossyConversion: true)
                let back = lossy.flatMap { String(data: $0, encoding: enc) }
                parts.append("\(strict?.count ?? -1)/\(lossy.map { $0.reduce(0) { ($0 &* 31) &+ Int($1) } } ?? -1)/\(back == s ? "=" : (back == nil ? "nil" : "~"))")
            }
            log("enc \(enc.rawValue) \(String.localizedName(of: enc)) \(parts.joined(separator: " "))")
        }

        // 2. String transforms (ICU transliteration)
        let transforms: [(String, StringTransform)] = [
            ("toLatin", .toLatin), ("mandarinToLatin", .mandarinToLatin), ("toUnicodeName", .toUnicodeName),
            ("latinToKatakana", .latinToKatakana), ("hiraganaToKatakana", .hiraganaToKatakana), ("latinToCyrillic", .latinToCyrillic),
            ("latinToGreek", .latinToGreen), ("latinToHangul", .latinToHangul), ("latinToArabic", .latinToArabic), ("latinToThai", .latinToThai),
            ("stripDiacritics", .stripDiacritics), ("stripCombiningMarks", .stripCombiningMarks), ("fullwidthToHalfwidth", .fullwidthToHalfwidth), ("toXMLHex", .toXMLHex),
        ]
        let transformSamples = ["Привет", "中文", "ひらがな", "konnichiwa", "Ελληνικά", "café ñ", "ＡＢＣ１２３", "😀 ©"]
        for (name, t) in transforms {
            for s in transformSamples {
                log("transform \(name) \(s) -> \(s.applyingTransform(t, reverse: false) ?? "nil") | rev -> \(s.applyingTransform(t, reverse: true) ?? "nil")")
            }
        }

        // 3. Regular expressions with Unicode word boundaries (word break iterator, dictionaries)
        let regexSamples = ["hello world foo", "我们是中国人", "日本語の文章です", "ภาษาไทยง่ายมาก", "ខ្មែរភាសា", "ພາສາລາວ"]
        for opts in [NSRegularExpression.Options(), .useUnicodeWordBoundaries] {
            let re = try NSRegularExpression(pattern: "\\b\\w+?\\b", options: opts)
            for s in regexSamples {
                let ns = s as NSString
                let words = re.matches(in: s, range: NSRange(location: 0, length: ns.length)).map { ns.substring(with: $0.range) }
                log("regex \(opts.rawValue) \(s) \(words)")
            }
        }

        // 4. Collation through NSString
        let words = ["Äpfel", "apple", "Zebra", "zebra", "ähnlich", "Ångström", "ch", "cz", "čaj", "日本", "中国", "한국", "ไทย", "file10", "file2"]
        for l in ["en_US", "de_DE", "sv_SE", "cs_CZ", "zh_CN", "ja_JP", "th_TH"] {
            let loc = Locale(identifier: l)
            log("sort \(l) \(words.sorted { $0.compare($1, options: [], range: nil, locale: loc) == .orderedAscending })")
        }
        log("std \(words.sorted { $0.localizedStandardCompare($1) == .orderedAscending })")

        // 5. Case mapping and formatting
        for l in ["en_US", "tr_TR", "th_TH", "zh_CN", "ja_JP", "de_DE", "ar_SA"] {
            let loc = Locale(identifier: l)
            log("case \(l) \("istanbul ılık 中文 english ภาษาไทย".capitalized(with: loc))")
            let df = DateFormatter(); df.locale = loc; df.dateStyle = .full; df.timeStyle = .long; df.timeZone = TimeZone(identifier: "UTC")
            log("date \(l) \(df.string(from: Date(timeIntervalSince1970: 1_800_000_000)))")
            let nf = NumberFormatter(); nf.locale = loc
            for style in [NumberFormatter.Style.decimal, .currency, .percent, .spellOut, .ordinal] {
                nf.numberStyle = style
                log("num \(l) \(style.rawValue) \(nf.string(from: 1234.5) ?? "nil")")
            }
        }

        // 6. Unit-backed formatting (ICU unit data)
        for l in ["en_US", "de_DE", "fr_FR", "ru_RU", "ja_JP", "ar_EG"] {
            let loc = Locale(identifier: l)
            log("duration \(l) \(Duration.seconds(3725).formatted(.units(allowed: [.hours, .minutes, .seconds], width: .wide).locale(loc)))")
            log("bytes \(l) \(ByteCountFormatter.string(fromByteCount: 1_234_567, countStyle: .file))")
        }

        try lines.joined(separator: "\n").write(toFile: path, atomically: true, encoding: .utf8)
        print("ICU probe wrote \(lines.count) lines to \(path)")
    }
}
