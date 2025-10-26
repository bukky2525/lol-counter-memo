#!/usr/bin/env python3
"""
items_data.jsonから不要なデータを削除して最適化
"""

import json
import re

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

def optimize_item(item):
    """アイテムデータを最適化"""
    optimized = {
        'id': item['id'],
        'name': item['name'],
        'price': item['price'],
        'sellPrice': item['sellPrice'],
        'category': item['category'],
        'subcategory': item['subcategory'],
        'stats': item['stats'],
        'tags': item['tags']
    }
    
    # 英語名がある場合のみ追加
    if item.get('englishName'):
        optimized['englishName'] = item['englishName']
    
    # 説明文がある場合のみ追加（HTMLタグを削除）
    if item.get('description'):
        clean_desc = clean_description(item['description'])
        if clean_desc:
            optimized['description'] = clean_desc
    
    # 簡易説明がある場合のみ追加
    if item.get('plaintext'):
        optimized['plaintext'] = item['plaintext']
    
    # 合成情報がある場合のみ追加
    if item.get('buildsFrom') and len(item['buildsFrom']) > 0:
        optimized['buildsFrom'] = item['buildsFrom']
    
    if item.get('buildsInto') and len(item['buildsInto']) > 0:
        optimized['buildsInto'] = item['buildsInto']
    
    return optimized

def main():
    """メイン処理"""
    print("items_data.jsonを読み込み中...")
    
    with open('items_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"元のアイテム数: {len(data['items'])}")
    print(f"元のファイルサイズ: {len(json.dumps(data, ensure_ascii=False))} 文字")
    
    # アイテムを最適化
    print("アイテムデータを最適化中...")
    optimized_items = []
    
    for item in data['items']:
        # 基本的なアイテムのみ保持（ID、名前、価格があるもの）
        if item.get('id') and item.get('name') and item.get('price') is not None:
            optimized_item = optimize_item(item)
            optimized_items.append(optimized_item)
    
    # 最適化されたデータを作成
    optimized_data = {
        'items': optimized_items,
        'categories': data['categories'],
        'version': data['version']
    }
    
    print(f"最適化後のアイテム数: {len(optimized_items)}")
    
    # 最適化されたファイルを保存
    with open('items_data.json', 'w', encoding='utf-8') as f:
        json.dump(optimized_data, f, ensure_ascii=False, indent=2)
    
    print(f"最適化後のファイルサイズ: {len(json.dumps(optimized_data, ensure_ascii=False))} 文字")
    
    # 削除されたアイテム数を表示
    removed_count = len(data['items']) - len(optimized_items)
    if removed_count > 0:
        print(f"削除されたアイテム数: {removed_count}")
    
    print("最適化完了！")

if __name__ == "__main__":
    main()
