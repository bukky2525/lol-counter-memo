import json
import re
import sys

# Windows PowerShellでのUnicode出力対応
sys.stdout.reconfigure(encoding='utf-8')

# 公式のチャンピオン名を読み込み
with open("official_champion_names.json", "r", encoding="utf-8") as f:
    official_data = json.load(f)
    official_names = set(official_data["names"])

# index.htmlからチャンピオン名を抽出
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# h3タグからチャンピオン名を抽出（カッコ内の情報を除く）
current_names_raw = re.findall(r'<h3[^>]*>(?:<img[^>]*>)?\s*([^<（]+)', html_content)
current_names = set([name.strip() for name in current_names_raw])

print("=" * 70)
print("現在のindex.htmlにあるチャンピオン名と公式名の比較")
print("=" * 70)
print()

# 間違っている名前を探す
incorrect_names = []
for name in current_names:
    if name not in official_names:
        # 類似の公式名を探す
        similar = [official for official in official_names if name[:2] in official or official[:2] in name]
        incorrect_names.append((name, similar))

if incorrect_names:
    print(f"❌ 修正が必要な名前: {len(incorrect_names)}件")
    print()
    for wrong, similar in incorrect_names:
        print(f"  修正前: {wrong}")
        if similar:
            print(f"  → 候補: {', '.join(similar)}")
        else:
            print(f"  → 公式名が見つかりません")
        print()
else:
    print("✅ すべてのチャンピオン名が公式と一致しています！")

print("=" * 70)
print("公式にあるが、index.htmlに含まれていないチャンピオン:")
print("=" * 70)
missing = official_names - current_names
if missing:
    for name in sorted(missing):
        print(f"  - {name}")
    print(f"\n合計: {len(missing)}体")
else:
    print("  なし")

print()
print("=" * 70)
print(f"公式チャンピオン総数: {len(official_names)}体")
print(f"index.htmlのチャンピオン数: {len(current_names)}体")
print("=" * 70)

