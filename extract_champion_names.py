import re
import json

# HTMLファイルのパスを指定
html_path = r"c:\Users\gogok\Downloads\チャンピオン - リーグ・オブ・レジェンド - ユニバース.html"

# HTMLファイルを読み込み
try:
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("ファイルが見つかりません。代わりに、提供されたHTMLから直接抽出します。")
    # 提供されたHTMLコンテンツから直接抽出
    content = """
    <h1>アイバーン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>アカリ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>アクシャン</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>アジール</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>アッシュ</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>アニビア</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>アニー</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>アフェリオス</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>アムム</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>アリスター</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>アンベッサ</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>アーゴット</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>アーリ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>イブリン</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>イラオイ</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>イレリア</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ウディア</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>ウーコン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>エイトロックス</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>エコー</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>エズリアル</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>エリス</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>オラフ</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>オリアナ</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>オレリオン・ソル</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>オーロラ</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>オーン</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>カイ＝サ</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>カサディン</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>カシオペア</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>カタリナ</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>カミール</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>カリスタ</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>カルマ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>カ・サンテ</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>カーサス</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>カ＝ジックス</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>ガリオ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ガレン</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ガングプランク</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>キヤナ</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>キンドレッド</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>クイン</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>クレッド</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>グウェン</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>グラガス</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>グレイブス</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>ケイトリン</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>ケイル</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ケイン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ケネン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>コグ＝マウ</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>コーキ</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>サイオン</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>サイラス</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>サミーラ</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ザイラ</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>ザック</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ザヤ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>シェン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>シャコ</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>シンジド</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>シンドラ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>シン・ジャオ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>シヴァーナ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>シヴィア</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>ジェイス</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>ジグス</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ジャックス</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ジャンナ</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ジャーヴァンⅣ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ジリアン</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ジン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ジンクス</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>スウェイン</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>スカーナー</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>スモルダー</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>スレッシュ</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>セジュアニ</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>セト</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>セナ</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>セラフィーン</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>ゼド</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ゼラス</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>ゼリ</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ソナ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ソラカ</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>ゾーイ</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>タム・ケンチ</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>タリック</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>タリヤ</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>タロン</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ダイアナ</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>ダリウス</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>チョ＝ガス</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>ツイステッド・フェイト</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>ティーモ</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>トゥイッチ</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>トランドル</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>トリスターナ</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>トリンダメア</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>ドクター・ムンド</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ドレイヴン</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ナサス</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>ナフィーリ</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>ナミ</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ナー</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>ニダリー</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>ニーコ</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>ニーラ</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>ヌヌ＆ウィルンプ</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>ノクターン</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ノーチラス</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>ハイマーディンガー</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>バード</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>パイク</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>パンテオン</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>ビクター</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>フィオラ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>フィズ</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>フィドルスティックス</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>フェイ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ブライアー</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ブラウム</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>ブラッドミア</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ブランド</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ブリッツクランク</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ヘカリム</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>ベイガー</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>ベル＝ヴェス</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>ボリベア</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>ポッピー</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>マオカイ</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>マスター・イー</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>マルザハール</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>マルファイト</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>ミス・フォーチュン</h1><h2><span data-gettext-identifier="faction-bilgewater">ビルジウォーター</span></h2>
    <h1>ミリオ</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>メル</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>モルガナ</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>モルデカイザー</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ヤスオ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ユナラ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ユーミ</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>ヨネ</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ヨリック</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>ライズ</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ラカン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ラックス</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ラムス</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>ランブル</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>リサンドラ</h1><h2><span data-gettext-identifier="faction-freljord">フレヨルド</span></h2>
    <h1>リリア</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>リヴェン</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>リー・シン</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ルシアン</h1><h2><span data-gettext-identifier="faction-unaffiliated-runeterra">ルーンテラ</span></h2>
    <h1>ルブラン</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>ルル</h1><h2><span data-gettext-identifier="faction-bandle-city">バンドルシティ</span></h2>
    <h1>レオナ</h1><h2><span data-gettext-identifier="faction-mount-targon">ターゴン</span></h2>
    <h1>レク＝サイ</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    <h1>レナータ・グラスク</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>レネクトン</h1><h2><span data-gettext-identifier="faction-shurima">シュリーマ</span></h2>
    <h1>レル</h1><h2><span data-gettext-identifier="faction-noxus">ノクサス</span></h2>
    <h1>レンガー</h1><h2><span data-gettext-identifier="faction-ixtal">イシュタル</span></h2>
    <h1>ワーウィック</h1><h2><span data-gettext-identifier="faction-zaun">ゾウン</span></h2>
    <h1>ヴァイ</h1><h2><span data-gettext-identifier="faction-piltover">ピルトーヴァー</span></h2>
    <h1>ヴァルス</h1><h2><span data-gettext-identifier="faction-ionia">アイオニア</span></h2>
    <h1>ヴィエゴ</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>ヴェイン</h1><h2><span data-gettext-identifier="faction-demacia">デマーシア</span></h2>
    <h1>ヴェックス</h1><h2><span data-gettext-identifier="faction-shadow-isles">シャドウアイル</span></h2>
    <h1>ヴェル＝コズ</h1><h2><span data-gettext-identifier="faction-void">ヴォイド</span></h2>
    """

# HTMLから日本語のチャンピオン名を抽出
champion_names = re.findall(r'<h1>([^<]+)</h1>', content)

# 日本語の文字を含むものだけをフィルタ
japanese_names = [name for name in champion_names if any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in name)]

# 重複を削除してソート
japanese_names = sorted(set(japanese_names))

print("公式Universeから抽出したチャンピオン名（日本語）:")
print(f"合計: {len(japanese_names)}体")
print("\n" + "=" * 50 + "\n")

for i, name in enumerate(japanese_names, 1):
    print(f"{i}. {name}")

# JSONファイルとして保存
output = {
    "count": len(japanese_names),
    "names": japanese_names
}

with open("official_champion_names.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 50)
print("official_champion_names.json に保存しました")

