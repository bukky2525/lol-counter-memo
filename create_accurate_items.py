#!/usr/bin/env python3
"""
LoL Guideのカテゴリ構造を参考にして、正確なアイテムデータを作成
"""

import json
import requests
import re

def create_accurate_items_data():
    """LoL Guideのカテゴリ構造に基づいて正確なアイテムデータを作成"""
    
    # LoL Guideのカテゴリ構造（実際のサイトから抽出）
    lol_guide_categories = {
        "START": {
            "name": "スタートアイテム",
            "subcategories": {
                "Lane": "レーン",
                "Jungle": "ジャングル"
            }
        },
        "BASIC": {
            "name": "基本アイテム", 
            "subcategories": {
                "Basic": "基本"
            }
        },
        "EPIC": {
            "name": "エピックアイテム",
            "subcategories": {
                "Epic": "エピック"
            }
        },
        "LEGENDARY": {
            "name": "レジェンダリーアイテム",
            "subcategories": {
                "Legendary": "レジェンダリー"
            }
        },
        "MYTHIC": {
            "name": "ミシックアイテム",
            "subcategories": {
                "Mythic": "ミシック"
            }
        },
        "BOOTS": {
            "name": "ブーツ",
            "subcategories": {
                "Boots": "ブーツ"
            }
        },
        "CONSUMABLE": {
            "name": "消費アイテム",
            "subcategories": {
                "Consumable": "消費"
            }
        },
        "WARD": {
            "name": "ワード",
            "subcategories": {
                "Trinket": "トリンケット"
            }
        },
        "JUNGLE": {
            "name": "ジャングル",
            "subcategories": {
                "Jungle": "ジャングル"
            }
        },
        "OTHER": {
            "name": "その他",
            "subcategories": {
                "Other": "その他"
            }
        }
    }
    
    # 最新のData Dragon APIからデータを取得
    url = "http://ddragon.leagueoflegends.com/cdn/15.21.1/data/en_US/item.json"
    
    try:
        print("最新APIからデータを取得中...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"取得したアイテム数: {len(data['data'])}")
        
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
                category, subcategory = determine_category_and_subcategory(item_data)
                
                item = {
                    'id': item_id,
                    'name': item_name,
                    'price': item_data['gold']['total'],
                    'sellPrice': item_data['gold']['sell'],
                    'category': category,
                    'subcategory': subcategory,
                    'stats': convert_stats(item_data.get('stats', {})),
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
        
        # 最終データ
        final_data = {
            'items': items,
            'categories': lol_guide_categories,
            'version': '15.21.1'
        }
        
        # UTF-8で保存
        with open('items_data_accurate.json', 'w', encoding='utf-8', newline='\n') as f:
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
            category_name = lol_guide_categories[category]['name']
            print(f"  {category_name}: {count}個")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def determine_category_and_subcategory(item_data):
    """LoL Guideのカテゴリ分類ロジックに基づいてカテゴリを決定"""
    tags = item_data.get('tags', [])
    price = item_data.get('gold', {}).get('total', 0)
    
    # ブーツ
    if 'Boots' in tags:
        return 'BOOTS', 'Boots'
    
    # 消費アイテム
    if 'Consumable' in tags:
        return 'CONSUMABLE', 'Consumable'
    
    # トリンケット（ワード）
    if 'Trinket' in tags:
        return 'WARD', 'Trinket'
    
    # ジャングル
    if 'Jungle' in tags:
        return 'JUNGLE', 'Jungle'
    
    # 価格に基づく分類（LoL Guideの分類ロジック）
    if price <= 500:
        # スタートアイテム
        if 'Lane' in tags:
            return 'START', 'Lane'
        elif 'Jungle' in tags:
            return 'START', 'Jungle'
        else:
            return 'BASIC', 'Basic'
    elif price <= 1500:
        # 基本アイテム
        return 'BASIC', 'Basic'
    elif price <= 3000:
        # エピックアイテム
        return 'EPIC', 'Epic'
    elif price <= 5000:
        # レジェンダリーアイテム
        return 'LEGENDARY', 'Legendary'
    else:
        # ミシックアイテム
        return 'MYTHIC', 'Mythic'

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

def convert_stats(stats):
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
            converted[japanese_key] = stat_value
    return converted

if __name__ == "__main__":
    create_accurate_items_data()
