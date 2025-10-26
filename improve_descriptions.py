#!/usr/bin/env python3
"""
アイテムの説明文を分かりやすく改善
"""

import json
import requests
import re

def improve_item_descriptions():
    """アイテムの説明文を分かりやすく改善"""
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
                    'tags': item_data.get('tags', [])
                }
                
                # 改善された説明文
                item['description'] = create_improved_description(item_data, item['stats'])
                
                if item_data.get('plaintext'):
                    item['plaintext'] = item_data['plaintext']
                
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
        with open('items_data_v3.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"改善された説明文で保存完了: {len(items)}個のアイテム")
        
        # サンプル表示
        print("\n改善された説明文の例:")
        for item in items[:5]:
            print(f"- {item['name']}: {item['description']}")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def create_improved_description(item_data, stats):
    """分かりやすい説明文を作成"""
    name = item_data['name']
    tags = item_data.get('tags', [])
    stats_list = []
    
    # ステータスを分かりやすく説明
    for stat_name, stat_value in stats.items():
        if stat_value > 0:
            if stat_name == '体力':
                stats_list.append(f"体力+{stat_value}")
            elif stat_name == 'マナ':
                stats_list.append(f"マナ+{stat_value}")
            elif stat_name == '物理防御':
                stats_list.append(f"物理防御+{stat_value}")
            elif stat_name == '魔法防御':
                stats_list.append(f"魔法防御+{stat_value}")
            elif stat_name == '攻撃力':
                stats_list.append(f"攻撃力+{stat_value}")
            elif stat_name == '魔法攻撃力':
                stats_list.append(f"魔法攻撃力+{stat_value}")
            elif stat_name == '移動速度':
                stats_list.append(f"移動速度+{stat_value}")
            elif stat_name == '攻撃速度':
                stats_list.append(f"攻撃速度+{stat_value}")
            elif stat_name == 'クリティカル率':
                stats_list.append(f"クリティカル率+{int(stat_value*100)}%")
            elif stat_name == '体力回復':
                stats_list.append(f"体力回復+{stat_value}")
            elif stat_name == 'マナ回復':
                stats_list.append(f"マナ回復+{stat_value}")
            elif stat_name == 'ライフステール':
                stats_list.append(f"ライフステール+{int(stat_value*100)}%")
            elif stat_name == 'クールダウン短縮':
                stats_list.append(f"クールダウン短縮+{int(stat_value*100)}%")
            else:
                stats_list.append(f"{stat_name}+{stat_value}")
    
    # タグに基づく説明
    description_parts = []
    
    if 'Boots' in tags:
        description_parts.append("移動速度向上")
    if 'Health' in tags:
        description_parts.append("体力強化")
    if 'Armor' in tags:
        description_parts.append("物理防御強化")
    if 'SpellBlock' in tags:
        description_parts.append("魔法防御強化")
    if 'Damage' in tags:
        description_parts.append("攻撃力強化")
    if 'SpellDamage' in tags:
        description_parts.append("魔法攻撃力強化")
    if 'CriticalStrike' in tags:
        description_parts.append("クリティカル強化")
    if 'AttackSpeed' in tags:
        description_parts.append("攻撃速度強化")
    if 'Lifesteal' in tags:
        description_parts.append("ライフステール")
    if 'CooldownReduction' in tags:
        description_parts.append("クールダウン短縮")
    if 'Mana' in tags:
        description_parts.append("マナ強化")
    if 'ManaRegen' in tags:
        description_parts.append("マナ回復強化")
    if 'HealthRegen' in tags:
        description_parts.append("体力回復強化")
    if 'Consumable' in tags:
        description_parts.append("消費アイテム")
    if 'Active' in tags:
        description_parts.append("アクティブ効果")
    
    # 説明文を組み立て
    if stats_list:
        main_desc = " ".join(stats_list)
    else:
        main_desc = " ".join(description_parts) if description_parts else "基本アイテム"
    
    return main_desc

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

def determine_subcategory(tags, category=None):
    """タグからサブカテゴリを決定"""
    if not tags:
        return "Active"
    
    subcategory_mapping = {
        'START': {'Lane': 'Lane', 'Jungle': 'Jungle'},
        'TOOLS': {'Consumable': 'Consumable', 'Goldper': 'Goldper', 'Vision': 'Vision'},
        'DEFENSE': {'Health': 'Health', 'Armor': 'Armor', 'SpellBlock': 'Spellblock', 'HealthRegen': 'Healthregen'},
        'ATTACK': {'Damage': 'Damage', 'CriticalStrike': 'Criticalstrike', 'AttackSpeed': 'Attackspeed', 'Lifesteal': 'Lifesteal'},
        'MAGIC': {'SpellDamage': 'Spelldamage', 'CooldownReduction': 'Cooldownreduction', 'Mana': 'Mana', 'ManaRegen': 'Manaregen'},
        'MOVEMENT': {'Boots': 'Boots', 'NonbootsMovement': 'Nonbootsmovement'},
        'UNCATEGORIZED': {'Active': 'Active', 'ArmorPenetration': 'Armorpenetration', 'Aura': 'Aura', 'MagicPenetration': 'Magicpenetration', 'OnHit': 'Onhit', 'Slow': 'Slow', 'Stealth': 'Stealth', 'Trinket': 'Trinket', 'SpellVamp': 'Spellvamp', 'Tenacity': 'Tenacity'}
    }
    
    category_mapping = subcategory_mapping.get(category or determine_category(tags), {})
    for tag in tags:
        if tag in category_mapping:
            return category_mapping[tag]
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
        'rFlatGoldPer10Mod': 'ゴールド獲得'
    }
    
    converted = {}
    for stat_key, stat_value in stats.items():
        if stat_value != 0:
            japanese_key = stat_mapping.get(stat_key, stat_key)
            converted[japanese_key] = stat_value
    return converted

if __name__ == "__main__":
    improve_item_descriptions()
