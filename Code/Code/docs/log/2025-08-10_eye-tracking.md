# 目トラッキング機能の追加

## 概要
内蔵/USB Webカメラを用いて、MediaPipe Face Mesh の虹彩ランドマークから視線方向（LEFT/RIGHT/UP/DOWN/CENTER）を推定し、フレーム上に可視化するシングルスクリプトを追加しました。

## 追加/変更ファイル
- 追加: `Code/EyeTracker.py`
- 追加: `Code/requirements.txt`

## 依存関係
- OpenCV (`opencv-python>=4.9`)
- NumPy (`numpy>=1.24`)

Windows PowerShell でのインストール例（Python 3.13 など MediaPipe 非対応環境向け）:

```
py -m pip install -r Code/requirements.txt
```

MediaPipe を利用できる Python（例: 3.10/3.11）を使う場合:

```
py -3.11 -m pip install -r Code/requirements-mediapipe.txt
```

## 使い方
実行:

```
py Code/EyeTracker.py
```

主なオプション:
- `--camera`: 使用するカメラ番号（既定: 0）
- `--width`, `--height`: 取得フレーム解像度（既定: 1280x720）
- `--smooth`: 視線相対座標の指数移動平均係数 0〜1（大きいほど滑らか、既定: 0.5）

実行中のキー操作:
- `c`: 現在の視線相対座標を「中央」としてキャリブレーション
- `q`: 終了

## 実装詳細（概要）
MediaPipe が利用可能な場合は Face Mesh（`refine_landmarks=True`）で以下のランドマークを利用:
- 眼領域ボックス: 左目 `LEFT_EYE_LANDMARKS`、右目 `RIGHT_EYE_LANDMARKS`
- 虹彩中心: 左 `LEFT_IRIS_LANDMARKS`、右 `RIGHT_IRIS_LANDMARKS`

眼領域の正規化座標内で虹彩中心の相対位置 `(x, y)` を 0〜1 に正規化し、しきい値
`x<0.35→LEFT / x>0.65→RIGHT / それ以外→CENTER`、`y<0.35→UP / y>0.65→DOWN / それ以外→CENTER`
で粗い視線方向を分類。座標は指数移動平均で平滑化。

MediaPipe が利用不可の場合は OpenCV の Haar 分類器で顔と目を検出し、閾値＋OTSU による二値化とモルフォロジーで瞳孔の最大輪郭重心を推定して相対座標化します。

## 既知の注意点/制約
- 強い逆光・暗所・フレーム落ちがあると精度が低下します。
- 眼鏡/反射/斜め顔などで虹彩が不検出になる場合があります。
- 本分類は粗い方向（5値）で、サッカード・瞳孔径は扱いません。

## 今後の展開（案）
- ユーザー固有キャリブレーション（画面座標への射影、回帰モデル導入）
- まばたき検出、注視時間の計測/ログ保存
- データ出力（OSC/WebSocket/HTTP）インターフェースの追加


