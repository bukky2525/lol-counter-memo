#!/usr/bin/env python3
"""
より詳細なアイテム情報を含むitems_data.jsonを作成
"""

import json
import requests
import re

def fetch_and_save_detailed_items():
    """詳細なアイテム情報を取得して保存"""
    url = "http://ddragon.leagueoflegends.com/cdn/15.17.1/data/ja_JP/item.json"
    
    try:
        print("APIからデータを取得中...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"取得したアイテム数: {len(data['data'])}")
        
        # アイテムを処理
        items = []
        for item_id, item_data in data['data'].items():
            # 基本的なアイテムのみ処理（価格が0より大きいもの）
            if item_data.get('name') and item_data.get('gold', {}).get('total', 0) > 0:
                item = {
                    'id': item_id,
                    'name': item_data['name'],
                    'price': item_data['gold']['total'],
                    'sellPrice': item_data['gold']['sell'],
                    'category': determine_category(item_data.get('tags', [])),
                    'subcategory': determine_subcategory(item_data.get('tags', [])),
                    'stats': convert_stats(item_data.get('stats', {})),
                    'tags': item_data.get('tags', []),
                    'fullDescription': clean_html(item_data.get('description', '')),  # 詳細説明
                    'plaintext': item_data.get('plaintext', '')  # 簡潔な説明
                }
                
                # 進化先と素材
                if item_data.get('from'):
                    item['buildsFrom'] = item_data['from']
                if item_data.get('into'):
                    item['buildsInto'] = item_data['into']
                    
                items.append(item)
        
        # カテゴリ情報
        categories = {
            "START": {"name": "スタート", "subcategories": {"Lane": "レーン", "Jungle": "ジャングル"}},
            "TOOLS": {"name": "ツール", "subcategories": {"Consumable": "消費アイテム", "Goldper": "ゴールド獲得", "Vision": "視界"}},
            "DEFENSE": {"name": "防御", "subcategories": {"Health": "体力", "Armor": "物理防御", "Spellblock": "魔法防御", "Healthregen": "体力回復"}},
            "ATTACK": {"name": "攻撃", "subcategories": {"Damage": "攻撃力", "Criticalstrike": "クリティカル", "Attackspeed": "攻撃速度", "Lifesteal": "ライフステール"}},
            "MAGIC": {"name": "魔法", "subcategories": {"Spelldamage": "魔法攻撃力", "Cooldownreduction": "クールダウン", "Mana": "マナ", "Manaregen": "マナ回復"}},
            "MOVEMENT": {"name": "移動", "subcategories": {"Boots": "ブーツ", "Nonbootsmovement": "移動速度"}},
            "UNCATEGORIZED": {"name": "その他", "subcategories": {"Active": "アクティブ", "Armorpenetration": "物理貫通", "Aura": "オーラ", "Magicpenetration": "魔法貫通", "Onhit": "オンヒット", "Slow": "スロー", "Stealth": "ステルス", "Trinket": "トリンケット", "Spellvamp": "スペルヴァンプ", "Tenacity": "テナシティ"}}
        }
        
        # 最終データ
        final_data = {
            'items': items,
            'categories': categories,
            'version': data['version']
        }
        
        # UTF-8で保存
        with open('items_data_final.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"保存完了: {len(items)}個のアイテム")
        
        # サンプル表示
        print("\n詳細情報を含むアイテムの例:")
        for item in items[:3]:
            print(f"- {item['name']}")
            print(f"  ステータス: {len(item['stats'])}個")
            print(f"  説明: {len(item['fullDescription'])}文字")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

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

def determine_category(tags):
    """タグからカテゴリを決定"""
    category_mapping = {
        'Boots': 'MOVEMENT',
        'Lane': 'START',
        'Jungle': 'START',
        'Consumable': 'TOOLS',
        'Goldper': 'TOOLS',
        'Vision': 'TOOLS',
        'Health': 'DEFENSE',
        'Armor': 'DEFENSE',
        'SpellBlock': 'DEFENSE',
        'HealthRegen': 'DEFENSE',
        'Damage': 'ATTACK',
        'CriticalStrike': 'ATTACK',
        'AttackSpeed': 'ATTACK',
        'Lifesteal': 'ATTACK',
        'SpellDamage': 'MAGIC',
        'CooldownReduction': 'MAGIC',
        'Mana': 'MAGIC',
        'ManaRegen': 'MAGIC',
        'NonbootsMovement': 'MOVEMENT',
        'Active': 'UNCATEGORIZED',
        'ArmorPenetration': 'UNCATEGORIZED',
        'Aura': 'UNCATEGORIZED',
        'MagicPenetration': 'UNCATEGORIZED',
        'OnHit': 'UNCATEGORIZED',
        'Slow': 'UNCATEGORIZED',
        'Stealth': 'UNCATEGORIZED',
        'Trinket': 'UNCATEGORIZED',
        'SpellVamp': 'UNCATEGORIZED',
        'Tenacity': 'UNCATEGORIZED'
    }
    
    for tag in tags:
        if tag in category_mapping:
            return category_mapping[tag]
    return "UNCATEGORIZED"

def determine_subcategory(tags):
    """タグからサブカテゴリを決定"""
    if not tags:
        return "Active"
    
    for tag in tags:
        if tag in ['Lane', 'Jungle', 'Consumable', 'Goldper', 'Vision', 
                   'Health', 'Armor', 'SpellBlock', 'HealthRegen',
                   'Damage', 'CriticalStrike', 'AttackSpeed', 'Lifesteal',
                   'SpellDamage', 'CooldownReduction', 'Mana', 'ManaRegen',
                   'Boots', 'NonbootsMovement', 'Active', 'ArmorPenetration',
                   'Aura', 'MagicPenetration', 'OnHit', 'Slow', 'Stealth',
                   'Trinket', 'SpellVamp', 'Tenacity']:
            return tag
    
    return "Active"

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
    fetch_and_save_detailed_items()
