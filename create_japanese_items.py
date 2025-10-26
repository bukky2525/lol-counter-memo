#!/usr/bin/env python3
"""
日本語のData Dragon API (15.17.1) を使用して正確なアイテムデータを作成
"""

import json
import requests
import re

def create_japanese_items_data():
    """日本語のData Dragon APIから正確なアイテムデータを作成"""
    
    # 日本語APIからデータを取得
    url = "http://ddragon.leagueoflegends.com/cdn/15.17.1/data/ja_JP/item.json"
    
    try:
        print("日本語APIからデータを取得中...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"取得したアイテム数: {len(data['data'])}")
        
        # tree構造からカテゴリ情報を取得
        tree = data.get('tree', [])
        category_mapping = {}
        
        for category in tree:
            header = category['header']
            tags = category['tags']
            category_mapping[header] = tags
        
        print("カテゴリマッピング:", category_mapping)
        
        # アイテムを処理（重複除去とカテゴリ分類）
        items = []
        seen_names = set()
        
        for item_id, item_data in data['data'].items():
            # 基本的なアイテムのみ処理（価格が0より大きいもの）
            if item_data.get('name') and item_data.get('gold', {}).get('total', 0) > 0:
                item_name = item_data['name']
                
                # 重複チェック
                if item_name in seen_names:
                    print(f"重複をスキップ: {item_name}")
                    continue
                
                seen_names.add(item_name)
                
                # カテゴリとサブカテゴリを決定
                category, subcategory = determine_category_from_tree(item_data, category_mapping)
                
                item = {
                    'id': item_id,
                    'name': item_name,
                    'price': item_data['gold']['total'],
                    'sellPrice': item_data['gold']['sell'],
                    'category': category,
                    'subcategory': subcategory,
                    'stats': convert_stats_to_japanese(item_data.get('stats', {})),
                    'tags': item_data.get('tags', []),
                    'fullDescription': clean_html(item_data.get('description', '')),
                    'plaintext': item_data.get('plaintext', '')
                }
                
                # 進化先と素材
                if item_data.get('from'):
                    item['buildsFrom'] = item_data['from']
                if item_data.get('into'):
                    item['buildsInto'] = item_data['into']
                    
                items.append(item)
        
        # LoL Guide準拠のカテゴリ情報
        categories = {
            "START": {"name": "スタートアイテム", "subcategories": {"Lane": "レーン", "Jungle": "ジャングル"}},
            "BASIC": {"name": "基本アイテム", "subcategories": {"Basic": "基本"}},
            "EPIC": {"name": "エピックアイテム", "subcategories": {"Epic": "エピック"}},
            "LEGENDARY": {"name": "レジェンダリーアイテム", "subcategories": {"Legendary": "レジェンダリー"}},
            "MYTHIC": {"name": "ミシックアイテム", "subcategories": {"Mythic": "ミシック"}},
            "BOOTS": {"name": "ブーツ", "subcategories": {"Boots": "ブーツ"}},
            "CONSUMABLE": {"name": "消費アイテム", "subcategories": {"Consumable": "消費"}},
            "WARD": {"name": "ワード", "subcategories": {"Trinket": "トリンケット"}},
            "JUNGLE": {"name": "ジャングル", "subcategories": {"Jungle": "ジャングル"}},
            "OTHER": {"name": "その他", "subcategories": {"Other": "その他"}}
        }
        
        # 最終データ
        final_data = {
            'items': items,
            'categories': categories,
            'version': '15.17.1'
        }
        
        # UTF-8で保存
        with open('items_data_japanese.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"保存完了: {len(items)}個のアイテム（重複除去済み）")
        
        # 重複チェック
        names = [item['name'] for item in items]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        print(f"重複アイテム: {len(duplicates)}個")
        if duplicates:
            print("重複例:", duplicates[:5])
        
        # カテゴリ別のアイテム数を表示
        category_counts = {}
        for item in items:
            category = item['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("\nカテゴリ別アイテム数:")
        for category, count in sorted(category_counts.items()):
            category_name = categories[category]['name']
            print(f"  {category_name}: {count}個")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def determine_category_from_tree(item_data, category_mapping):
    """tree構造に基づいてカテゴリを決定"""
    tags = item_data.get('tags', [])
    price = item_data.get('gold', {}).get('total', 0)
    
    # tree構造のカテゴリをチェック
    for category, category_tags in category_mapping.items():
        if any(tag in tags for tag in category_tags):
            if category == "START":
                if "LANE" in tags:
                    return "START", "Lane"
                elif "JUNGLE" in tags:
                    return "START", "Jungle"
                else:
                    return "START", "Lane"
            elif category == "MOVEMENT":
                return "BOOTS", "Boots"
            elif category == "TOOLS":
                if "CONSUMABLE" in tags:
                    return "CONSUMABLE", "Consumable"
                elif "VISION" in tags:
                    return "WARD", "Trinket"
                else:
                    return "OTHER", "Other"
            elif category == "DEFENSE":
                return "LEGENDARY", "Legendary"
            elif category == "ATTACK":
                return "LEGENDARY", "Legendary"
            elif category == "MAGIC":
                return "LEGENDARY", "Legendary"
            elif category == "UNCATEGORIZED":
                return "OTHER", "Other"
    
    # 価格に基づく分類（フォールバック）
    if price <= 500:
        return "START", "Lane"
    elif price <= 1500:
        return "BASIC", "Basic"
    elif price <= 3000:
        return "EPIC", "Epic"
    elif price <= 5000:
        return "LEGENDARY", "Legendary"
    else:
        return "MYTHIC", "Mythic"

def clean_html(text):
    """HTMLタグを削除してクリーンなテキストに"""
    if not text:
        return ""
    
    # <br>を改行に変換
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    
    # HTMLタグを削除
    text = re.sub(r'<[^>]+>', '', text)
    
    # 特殊文字をエスケープ
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # 余分な改行を整理
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def convert_stats_to_japanese(stats):
    """ステータスを日本語に変換"""
    stat_mapping = {
        'FlatHPPoolMod': '体力',
        'FlatMPPoolMod': 'マナ',
        'FlatArmorMod': '物理防御',
        'FlatSpellBlockMod': '魔法防御',
        'FlatPhysicalDamageMod': '攻撃力',
        'FlatMagicDamageMod': '魔法攻撃力',
        'FlatMovementSpeedMod': '移動速度',
        'FlatAttackSpeedMod': '攻撃速度',
        'FlatCritChanceMod': 'クリティカル率',
        'FlatCritDamageMod': 'クリティカルダメージ',
        'FlatHPRegenMod': '体力回復',
        'FlatMPRegenMod': 'マナ回復',
        'rFlatArmorPenetrationMod': '物理貫通',
        'rFlatMagicPenetrationMod': '魔法貫通',
        'PercentLifeStealMod': 'ライフステール',
        'PercentSpellVampMod': 'スペルヴァンプ',
        'rPercentCooldownMod': 'クールダウン短縮',
        'rFlatGoldPer10Mod': 'ゴールド獲得',
        'PercentMovementSpeedMod': '移動速度%',
        'PercentAttackSpeedMod': '攻撃速度%',
        'PercentPhysicalDamageMod': '攻撃力%',
        'PercentMagicDamageMod': '魔法攻撃力%',
        'PercentEXPBonus': '経験値ボーナス%'
    }
    
    converted = {}
    for stat_key, stat_value in stats.items():
        if stat_value != 0:
            japanese_key = stat_mapping.get(stat_key, stat_key)
            # パーセンテージ値を適切に表示
            if 'Percent' in stat_key or 'CritChance' in stat_key:
                converted[japanese_key] = f"{stat_value * 100:.0f}%"
            else:
                converted[japanese_key] = stat_value
    return converted

if __name__ == "__main__":
    create_japanese_items_data()
