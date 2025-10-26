#!/usr/bin/env python3
"""
最新のData Dragon API (15.21.1) からアイテムデータを取得して重複を除去
"""

import json
import requests
import re

def fetch_and_save_latest_items():
    """最新のアイテム情報を取得して重複を除去して保存"""
    url = "http://ddragon.leagueoflegends.com/cdn/15.21.1/data/en_US/item.json"
    
    try:
        print("最新APIからデータを取得中...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"取得したアイテム数: {len(data['data'])}")
        
        # アイテムを処理（重複除去）
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
                
                item = {
                    'id': item_id,
                    'name': item_name,
                    'price': item_data['gold']['total'],
                    'sellPrice': item_data['gold']['sell'],
                    'category': determine_category(item_data.get('tags', [])),
                    'subcategory': determine_subcategory(item_data.get('tags', [])),
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
        
        # カテゴリ情報（LoL Guide準拠）
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
            'version': '15.21.1'
        }
        
        # UTF-8で保存
        with open('items_data_latest.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"保存完了: {len(items)}個のアイテム（重複除去済み）")
        
        # 重複チェック
        names = [item['name'] for item in items]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        print(f"重複アイテム: {len(duplicates)}個")
        if duplicates:
            print("重複例:", duplicates[:5])
        
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
    """タグからカテゴリを決定（LoL Guide準拠）"""
    if not tags:
        return "OTHER"
    
    # ブーツ
    if 'Boots' in tags:
        return "BOOTS"
    
    # 消費アイテム
    if 'Consumable' in tags:
        return "CONSUMABLE"
    
    # トリンケット（ワード）
    if 'Trinket' in tags:
        return "WARD"
    
    # ジャングル
    if 'Jungle' in tags:
        return "JUNGLE"
    
    # 価格に基づく分類（簡易版）
    # 実際の価格は後で設定されるため、タグベースで分類
    if 'Lane' in tags or 'Jungle' in tags:
        return "START"
    
    # その他はOTHER
    return "OTHER"

def determine_subcategory(tags):
    """タグからサブカテゴリを決定"""
    if not tags:
        return "Other"
    
    for tag in tags:
        if tag in ['Boots', 'Consumable', 'Trinket', 'Jungle', 'Lane']:
            return tag
    
    return "Other"

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
    fetch_and_save_latest_items()
