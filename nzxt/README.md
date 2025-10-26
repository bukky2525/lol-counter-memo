# NZXT Kraken ディスプレイ制御プロジェクト

NZXT KrakenシリーズのCPUクーラーに搭載されたLCDディスプレイをカスタマイズするPythonプロジェクトです。

## 機能

- **システム情報表示**: CPU温度、使用率、GPU温度、メモリ使用率
- **カスタムテキスト表示**: 任意のテキストメッセージ
- **画像表示**: カスタム画像やGIFアニメーション
- **リアルタイムモニタリング**: システム状態の動的表示
- **ゲーム統合**: ゲーム情報の表示

## 必要なハードウェア

- NZXT Kraken X53/Z53/X63/Z63/X73/Z73 シリーズ
- Windows 10/11
- Python 3.8以上

## セットアップ

1. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

2. NZXT CAMソフトウェアのインストール

3. スクリプトの実行:
```bash
python main.py
```

## 使用方法

### 基本的なシステム情報表示
```bash
python system_monitor.py
```

### カスタムテキスト表示
```bash
python custom_text.py "Hello World!"
```

### 画像表示
```bash
python image_display.py path/to/image.png
```

## 注意事項

- NZXT CAMソフトウェアが起動している必要があります
- 一部の機能は管理者権限が必要な場合があります
- ハードウェアの保証に影響する可能性があります

## ライセンス

MIT License
