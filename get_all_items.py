#!/usr/bin/env python3
"""
Riot Games Data Dragon APIから全アイテムデータを取得してJSONに変換
"""

import json
import requests
import re

def fetch_items_data():
    """Riot Games Data Dragon APIからアイテムデータを取得"""
    url = "http://ddragon.leagueoflegends.com/cdn/15.17.1/data/ja_JP/item.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"APIからのデータ取得に失敗しました: {e}")
        return None

def clean_description(description):
    """説明文からHTMLタグを削除して簡潔にする"""
    if not description:
        return ""
    
    # HTMLタグを削除
    clean = re.sub(r'<[^>]+>', '', description)
    # 連続する空白を1つに
    clean = re.sub(r'\s+', ' ', clean)
    # 前後の空白を削除
    clean = clean.strip()
    
    return clean

def convert_stat_key(stat_key):
    """ステータスキーを日本語に変換"""
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
        'PercentHPPoolMod': '体力%',
        'PercentMPPoolMod': 'マナ%',
        'PercentArmorMod': '物理防御%',
        'PercentSpellBlockMod': '魔法防御%',
        'PercentPhysicalDamageMod': '攻撃力%',
        'PercentMagicDamageMod': '魔法攻撃力%',
        'PercentMovementSpeedMod': '移動速度%',
        'PercentAttackSpeedMod': '攻撃速度%',
        'PercentCritChanceMod': 'クリティカル率%',
        'PercentCritDamageMod': 'クリティカルダメージ%',
        'PercentHPRegenMod': '体力回復%',
        'PercentMPRegenMod': 'マナ回復%',
        'rPercentArmorPenetrationMod': '物理貫通%',
        'rPercentMagicPenetrationMod': '魔法貫通%',
        'rPercentCooldownModPerLevel': 'クールダウン短縮/レベル',
        'rFlatHPModPerLevel': '体力/レベル',
        'rFlatMPModPerLevel': 'マナ/レベル',
        'rFlatArmorModPerLevel': '物理防御/レベル',
        'rFlatSpellBlockModPerLevel': '魔法防御/レベル',
        'rFlatPhysicalDamageModPerLevel': '攻撃力/レベル',
        'rFlatMagicDamageModPerLevel': '魔法攻撃力/レベル',
        'rFlatMovementSpeedModPerLevel': '移動速度/レベル',
        'rFlatAttackSpeedModPerLevel': '攻撃速度/レベル',
        'rFlatCritChanceModPerLevel': 'クリティカル率/レベル',
        'rFlatCritDamageModPerLevel': 'クリティカルダメージ/レベル',
        'rFlatHPRegenModPerLevel': '体力回復/レベル',
        'rFlatMPRegenModPerLevel': 'マナ回復/レベル',
        'rFlatArmorPenetrationModPerLevel': '物理貫通/レベル',
        'rFlatMagicPenetrationModPerLevel': '魔法貫通/レベル',
        'rFlatGoldPer10Mod': 'ゴールド獲得/10秒',
        'FlatEXPBonus': '経験値ボーナス',
        'PercentEXPBonus': '経験値ボーナス%',
        'rFlatTimeDeadMod': '死亡時間短縮',
        'rFlatTimeDeadModPerLevel': '死亡時間短縮/レベル',
        'rPercentTimeDeadMod': '死亡時間短縮%',
        'rPercentTimeDeadModPerLevel': '死亡時間短縮%/レベル',
        'FlatEnergyRegenMod': 'エネルギー回復',
        'rFlatEnergyRegenModPerLevel': 'エネルギー回復/レベル',
        'FlatEnergyPoolMod': 'エネルギー',
        'rFlatEnergyModPerLevel': 'エネルギー/レベル',
        'FlatDodgeMod': '回避',
        'rFlatDodgeModPerLevel': '回避/レベル',
        'PercentDodgeMod': '回避%',
        'FlatBlockMod': 'ブロック',
        'PercentBlockMod': 'ブロック%'
    }
    return stat_mapping.get(stat_key, stat_key)

def determine_category(tags):
    """タグからカテゴリを決定"""
    if not tags:
        return "UNCATEGORIZED"
    
    # タグの優先順位
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

def determine_subcategory(tags, category=None):
    """タグからサブカテゴリを決定"""
    if not tags:
        return "Active"
    
    # カテゴリ別のサブカテゴリマッピング
    subcategory_mapping = {
        'START': {
            'Lane': 'Lane',
            'Jungle': 'Jungle'
        },
        'TOOLS': {
            'Consumable': 'Consumable',
            'Goldper': 'Goldper',
            'Vision': 'Vision'
        },
        'DEFENSE': {
            'Health': 'Health',
            'Armor': 'Armor',
            'SpellBlock': 'Spellblock',
            'HealthRegen': 'Healthregen'
        },
        'ATTACK': {
            'Damage': 'Damage',
            'CriticalStrike': 'Criticalstrike',
            'AttackSpeed': 'Attackspeed',
            'Lifesteal': 'Lifesteal'
        },
        'MAGIC': {
            'SpellDamage': 'Spelldamage',
            'CooldownReduction': 'Cooldownreduction',
            'Mana': 'Mana',
            'ManaRegen': 'Manaregen'
        },
        'MOVEMENT': {
            'Boots': 'Boots',
            'NonbootsMovement': 'Nonbootsmovement'
        },
        'UNCATEGORIZED': {
            'Active': 'Active',
            'ArmorPenetration': 'Armorpenetration',
            'Aura': 'Aura',
            'MagicPenetration': 'Magicpenetration',
            'OnHit': 'Onhit',
            'Slow': 'Slow',
            'Stealth': 'Stealth',
            'Trinket': 'Trinket',
            'SpellVamp': 'Spellvamp',
            'Tenacity': 'Tenacity'
        }
    }
    
    category_mapping = subcategory_mapping.get(category or determine_category(tags), {})
    for tag in tags:
        if tag in category_mapping:
            return category_mapping[tag]
    
    return "Active"

def convert_items_data(api_data):
    """APIデータをアプリ用の形式に変換"""
    items = []
    
    for item_id, item_data in api_data['data'].items():
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
                'tags': item_data.get('tags', [])
            }
            
            # オプション項目
            if item_data.get('description'):
                clean_desc = clean_description(item_data['description'])
                if clean_desc:
                    item['description'] = clean_desc
            
            if item_data.get('plaintext'):
                item['plaintext'] = item_data['plaintext']
            
            if item_data.get('from'):
                item['buildsFrom'] = item_data['from']
            
            if item_data.get('into'):
                item['buildsInto'] = item_data['into']
                
            items.append(item)
    
    # カテゴリ情報
    categories = {
        "START": {
            "name": "スタート",
            "subcategories": {
                "Lane": "レーン",
                "Jungle": "ジャングル"
            }
        },
        "TOOLS": {
            "name": "ツール",
            "subcategories": {
                "Consumable": "消費アイテム",
                "Goldper": "ゴールド獲得",
                "Vision": "視界"
            }
        },
        "DEFENSE": {
            "name": "防御",
            "subcategories": {
                "Health": "体力",
                "Armor": "物理防御",
                "Spellblock": "魔法防御",
                "Healthregen": "体力回復"
            }
        },
        "ATTACK": {
            "name": "攻撃",
            "subcategories": {
                "Damage": "攻撃力",
                "Criticalstrike": "クリティカル",
                "Attackspeed": "攻撃速度",
                "Lifesteal": "ライフステール"
            }
        },
        "MAGIC": {
            "name": "魔法",
            "subcategories": {
                "Spelldamage": "魔法攻撃力",
                "Cooldownreduction": "クールダウン",
                "Mana": "マナ",
                "Manaregen": "マナ回復"
            }
        },
        "MOVEMENT": {
            "name": "移動",
            "subcategories": {
                "Boots": "ブーツ",
                "Nonbootsmovement": "移動速度"
            }
        },
        "UNCATEGORIZED": {
            "name": "その他",
            "subcategories": {
                "Active": "アクティブ",
                "Armorpenetration": "物理貫通",
                "Aura": "オーラ",
                "Magicpenetration": "魔法貫通",
                "Onhit": "オンヒット",
                "Slow": "スロー",
                "Stealth": "ステルス",
                "Trinket": "トリンケット",
                "Spellvamp": "スペルヴァンプ",
                "Tenacity": "テナシティ"
            }
        }
    }
    
    return {
        'items': items,
        'categories': categories,
        'version': api_data['version']
    }

def convert_stats(stats):
    """ステータスを日本語に変換"""
    converted = {}
    for stat_key, stat_value in stats.items():
        if stat_value != 0:  # 0の値は除外
            japanese_key = convert_stat_key(stat_key)
            converted[japanese_key] = stat_value
    return converted

def main():
    """メイン処理"""
    print("Riot Games Data Dragon APIからアイテムデータを取得中...")
    
    # APIからデータを取得
    api_data = fetch_items_data()
    if not api_data:
        print("データの取得に失敗しました")
        return
    
    print(f"APIバージョン: {api_data['version']}")
    print(f"アイテム数: {len(api_data['data'])}")
    
    # データを変換
    print("データを変換中...")
    converted_data = convert_items_data(api_data)
    
    # JSONファイルに保存
    output_file = 'items_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)
    
    print(f"変換完了！{output_file}に保存しました")
    print(f"アイテム数: {len(converted_data['items'])}")
    print(f"カテゴリ数: {len(converted_data['categories'])}")

if __name__ == "__main__":
    main()
