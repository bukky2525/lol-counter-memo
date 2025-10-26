/**
 * 文字変換ユーティリティ関数
 */

// カタカナをひらがなに変換
function katakanaToHiragana(str) {
    return str.replace(/[\u30a1-\u30f6]/g, match => {
        const chr = match.charCodeAt(0) - 0x60;
        return String.fromCharCode(chr);
    });
}

// ひらがなをカタカナに変換
function hiraganaToKatakana(str) {
    return str.replace(/[\u3041-\u3096]/g, match => {
        const chr = match.charCodeAt(0) + 0x60;
        return String.fromCharCode(chr);
    });
}

// ローマ字をひらがなに変換（訓令式・ヘボン式両対応）
function romajiToHiragana(str) {
    // cをkに変換（cha, chi以外）
    let result = str.toLowerCase().replace(/c(?![hyi])/g, 'k');
    
    // 3文字の組み合わせ
    const threeCharMap = {
        'kya':'きゃ','kyu':'きゅ','kyo':'きょ',
        'sha':'しゃ','shu':'しゅ','sho':'しょ',
        'sya':'しゃ','syu':'しゅ','syo':'しょ',
        'cha':'ちゃ','chu':'ちゅ','cho':'ちょ',
        'cya':'ちゃ','cyu':'ちゅ','cyo':'ちょ',
        'tya':'ちゃ','tyu':'ちゅ','tyo':'ちょ',
        'nya':'にゃ','nyu':'にゅ','nyo':'にょ',
        'hya':'ひゃ','hyu':'ひゅ','hyo':'ひょ',
        'mya':'みゃ','myu':'みゅ','myo':'みょ',
        'rya':'りゃ','ryu':'りゅ','ryo':'りょ',
        'gya':'ぎゃ','gyu':'ぎゅ','gyo':'ぎょ',
        'zya':'じゃ','zyu':'じゅ','zyo':'じょ',
        'jya':'じゃ','jyu':'じゅ','jyo':'じょ',
        'bya':'びゃ','byu':'びゅ','byo':'びょ',
        'pya':'ぴゃ','pyu':'ぴゅ','pyo':'ぴょ',
        'tsu':'つ','chi':'ち','shi':'し'
    };
    
    // 2文字の組み合わせ
    const twoCharMap = {
        'ka':'か','ki':'き','ku':'く','ke':'け','ko':'こ',
        'ca':'か','ci':'し','cu':'く','ce':'せ','co':'こ',
        'sa':'さ','si':'し','su':'す','se':'せ','so':'そ',
        'ta':'た','ti':'ち','tu':'つ','te':'て','to':'と',
        'na':'な','ni':'に','nu':'ぬ','ne':'ね','no':'の',
        'ha':'は','hi':'ひ','hu':'ふ','he':'へ','ho':'ほ',
        'ma':'ま','mi':'み','mu':'む','me':'め','mo':'も',
        'ya':'や','yu':'ゆ','yo':'よ',
        'ra':'ら','ri':'り','ru':'る','re':'れ','ro':'ろ',
        'wa':'わ','wo':'を',
        'ga':'が','gi':'ぎ','gu':'ぐ','ge':'げ','go':'ご',
        'za':'ざ','zi':'じ','zu':'ず','ze':'ぜ','zo':'ぞ',
        'da':'だ','di':'ぢ','du':'づ','de':'で','do':'ど',
        'ba':'ば','bi':'び','bu':'ぶ','be':'べ','bo':'ぼ',
        'pa':'ぱ','pi':'ぴ','pu':'ぷ','pe':'ぺ','po':'ぽ',
        'ja':'じゃ','ji':'じ','ju':'じゅ','jo':'じょ',
        'fa':'ふぁ','fi':'ふぃ','fu':'ふ','fe':'ふぇ','fo':'ふぉ',
        'va':'ゔぁ','vi':'ゔぃ','vu':'ゔ','ve':'ゔぇ','vo':'ゔぉ',
        'nn':'ん','n\'':'ん'
    };
    
    // 1文字
    const oneCharMap = {
        'a':'あ','i':'い','u':'う','e':'え','o':'お',
        'n':'ん'
    };
    
    let hiragana = '';
    let i = 0;
    
    while (i < result.length) {
        // 3文字チェック
        let threeChar = result.substring(i, i + 3);
        if (threeCharMap[threeChar]) {
            hiragana += threeCharMap[threeChar];
            i += 3;
            continue;
        }
        
        // 2文字チェック
        let twoChar = result.substring(i, i + 2);
        if (twoCharMap[twoChar]) {
            hiragana += twoCharMap[twoChar];
            i += 2;
            continue;
        }
        
        // 促音（っ）のチェック
        let nextChar = result.charAt(i + 1);
        if (result.charAt(i) === nextChar && nextChar !== '' && 'kstpbgzdjfhc'.includes(nextChar)) {
            hiragana += 'っ';
            i++;
            continue;
        }
        
        // 1文字チェック
        let oneChar = result.charAt(i);
        if (oneCharMap[oneChar]) {
            hiragana += oneCharMap[oneChar];
            i++;
            continue;
        }
        
        // マッチしない場合はそのまま
        hiragana += oneChar;
        i++;
    }
    
    return hiragana;
}

// カタカナをローマ字に変換（ヘボン式）
function katakanaToRomaji(str) {
    const kanaMap = {
        'ア':'a','イ':'i','ウ':'u','エ':'e','オ':'o',
        'カ':'ka','キ':'ki','ク':'ku','ケ':'ke','コ':'ko',
        'サ':'sa','シ':'shi','ス':'su','セ':'se','ソ':'so',
        'タ':'ta','チ':'chi','ツ':'tsu','テ':'te','ト':'to',
        'ナ':'na','ニ':'ni','ヌ':'nu','ネ':'ne','ノ':'no',
        'ハ':'ha','ヒ':'hi','フ':'fu','ヘ':'he','ホ':'ho',
        'マ':'ma','ミ':'mi','ム':'mu','メ':'me','モ':'mo',
        'ヤ':'ya','ユ':'yu','ヨ':'yo',
        'ラ':'ra','リ':'ri','ル':'ru','レ':'re','ロ':'ro',
        'ワ':'wa','ヲ':'wo','ン':'n',
        'ガ':'ga','ギ':'gi','グ':'gu','ゲ':'ge','ゴ':'go',
        'ザ':'za','ジ':'ji','ズ':'zu','ゼ':'ze','ゾ':'zo',
        'ダ':'da','ヂ':'ji','ヅ':'zu','デ':'de','ド':'do',
        'バ':'ba','ビ':'bi','ブ':'bu','ベ':'be','ボ':'bo',
        'パ':'pa','ピ':'pi','プ':'pu','ペ':'pe','ポ':'po',
        'ァ':'a','ィ':'i','ゥ':'u','ェ':'e','ォ':'o',
        'ャ':'ya','ュ':'yu','ョ':'yo','ッ':'',
        'ー':'','・':'',
        'ヴ':'vu','ヴァ':'va','ヴィ':'vi','ヴェ':'ve','ヴォ':'vo'
    };
    
    let romaji = '';
    for (let i = 0; i < str.length; i++) {
        // 2文字の組み合わせをチェック
        const twoChar = str.substring(i, i + 2);
        if (kanaMap[twoChar]) {
            romaji += kanaMap[twoChar];
            i++; // 2文字分進める
        } else {
            const char = str[i];
            romaji += kanaMap[char] || char;
        }
    }
    return romaji.toLowerCase();
}

