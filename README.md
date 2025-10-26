# LOL カウンターピック メモ

League of Legends（LoL）の全チャンピオンのカウンターピック情報をまとめたWebアプリケーションです。

🌐 **デモサイト**: [https://lol-counter-memo.netlify.app/](https://lol-counter-memo.netlify.app/)

## 機能

- 📊 **90以上のチャンピオン**のカウンター情報を収録
- 🖼️ **チャンピオン画像**: Data Dragon APIから公式アイコンを表示
- 🔍 **検索機能**: チャンピオン名で素早く検索
- 🎯 **レーンフィルター**: トップ、ジャングル、ミッド、ボット、サポート別に絞り込み
- 📱 **レスポンシブデザイン**: スマートフォンでも快適に閲覧可能
- 🌐 **完全日本語対応**

## 使い方

1. `index.html`をブラウザで開く
2. 検索ボックスでチャンピオン名を入力
3. レーンボタンでフィルタリング
4. カウンターピック情報を確認

## ファイル構成

- `index.html` - メインのHTMLファイル
- `counter_data.json` - カウンターデータ（JSON形式）
- `champion_images.json` - チャンピオン名と画像のマッピング
- `official_champion_names.json` - 公式チャンピオン名リスト
- `netlify.toml` - Netlifyデプロイ設定
- `test_images.html` - 画像読み込みテストページ
- `extract_champion_names.py` - チャンピオン名抽出スクリプト
- `fix_champion_names.py` - チャンピオン名修正スクリプト
- `compare_names.py` - チャンピオン名比較スクリプト

## データの更新方法

カウンターデータを更新する場合は、`counter_data.json`を編集してください。

```json
{
  "チャンピオン名": [
    {
      "lane": "top",
      "counters": ["カウンター1", "カウンター2", "..."]
    }
  ]
}
```

## 技術スタック

- HTML5
- CSS3
- JavaScript (Vanilla)
- JSON

## ライセンス

このプロジェクトは個人用のメモとして作成されています。

## 注意事項

- カウンター情報はメタの変化により変わる可能性があります
- あくまで参考情報としてご利用ください

