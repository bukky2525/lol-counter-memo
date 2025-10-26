#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# League of Legends Champion Counter Data Updater
# This script updates the HTML file with correct champion names and images

import re

# Champion name mapping from English to Japanese (based on official LoL site)
champion_mapping = {
    'Aatrox': 'アートロックス',
    'Ahri': 'アーリ',
    'Akali': 'アカリ',
    'Akshan': 'アクシャ',
    'Alistar': 'アリスター',
    'Amumu': 'アムム',
    'Annie': 'アニー',
    'Ashe': 'アッシュ',
    'Aurelion Sol': 'オーレリオン・ソル',
    'Blitzcrank': 'ブリッツクランキング',
    'Brand': 'ブランド',
    'Braum': 'ブラウム',
    'Caitlyn': 'ケイトリン',
    'Camille': 'カミール',
    'Corki': 'コーキー',
    'Darius': 'ダリウス',
    'Diana': 'ダイアナ',
    'Dr. Mundo': 'ドクター・ムンド',
    'Draven': 'ドレイヴン',
    'Ekko': 'エコー',
    'Evelynn': 'エヴリン',
    'Ezreal': 'エズリアル',
    'Fiddlesticks': 'フィドルスティックス',
    'Fiora': 'フィオラ',
    'Fizz': 'フィズ',
    'Galio': 'ガリオ',
    'Garen': 'ガレン',
    'Gnar': 'グナー',
    'Gragas': 'グラガス',
    'Graves': 'グレイブス',
    'Gwen': 'グウェン',
    'Hecarim': 'ヘカリム',
    'Heimerdinger': 'ハイマーディンガー',
    'Irelia': 'イレリア',
    'Janna': 'ジャナ',
    'Jarvan IV': 'ジャーヴァンⅣ',
    'Jax': 'ジャックス',
    'Jayce': 'ジェイス',
    'Jhin': 'ジン',
    'Jinx': 'ジンクス',
    'Kai\'Sa': 'カイ＝サ',
    'Kalista': 'カリスタ',
    'Karma': 'カルマ',
    'Kassadin': 'カサディン',
    'Katarina': 'カタリナ',
    'Kayle': 'ケイル',
    'Kayn': 'ケイン',
    'Kennen': 'ケネン',
    'Kha\'Zix': 'カズィックス',
    'Kindred': 'キンドレッド',
    'Lee Sin': 'リー・シン',
    'Leona': 'レオナ',
    'Lillia': 'リリア',
    'Lissandra': 'リサンドラ',
    'Lucian': 'ルシアン',
    'Lulu': 'ルル',
    'Lux': 'ラックス',
    'Master Yi': 'マスターヤイ',
    'Malphite': 'マルファイト',
    'Maokai': 'マオカイ',
    'Milio': 'ミリオ',
    'Miss Fortune': 'ミス・フォーチュン',
    'Mordekaiser': 'モルデカイザー',
    'Morgana': 'モルガナ',
    'Nami': 'ナミ',
    'Nasus': 'ナサス',
    'Nautilus': 'ノーチラス',
    'Nilah': 'ニーラ',
    'Nunu': 'ヌヌ',
    'Olaf': 'オラフ',
    'Orianna': 'オリアナ',
    'Ornn': 'オーン',
    'Pantheon': 'パンテオン',
    'Pyke': 'パイク',
    'Rakan': 'ラカン',
    'Rammus': 'ラモス',
    'Renekton': 'レネクトン',
    'Rengar': 'レンガー',
    'Riven': 'リヴェン',
    'Rumble': 'ランブル',
    'Samira': 'サミラ',
    'Senna': 'セナ',
    'Seraphine': 'セラフィーヌ',
    'Sett': 'セット',
    'Shyvana': 'シャイバナ',
    'Singed': 'シンジド',
    'Sion': 'サイオン',
    'Sivir': 'シヴィル',
    'Sona': 'ソナ',
    'Soraka': 'ソラカ',
    'Swain': 'スウェイン',
    'Syndra': 'シンドラ',
    'Talon': 'タロン',
    'Teemo': 'ティーモ',
    'Thresh': 'スレッシュ',
    'Tristana': 'トリスターナ',
    'Tryndamere': 'トラインダムアー',
    'Twisted Fate': 'ツイステッド・フェイト',
    'Twitch': 'ツイッチ',
    'Urgot': 'ウルゴット',
    'Varus': 'ヴァルス',
    'Vayne': 'ヴェイン',
    'Veigar': 'ベイガー',
    'Vex': 'ヴェックス',
    'Vi': 'ヴィ',
    'Viego': 'ビエゴ',
    'Viktor': 'ヴィクター',
    'Vladimir': 'ヴラディミール',
    'Volibear': 'ボリベア',
    'Warwick': 'ウォーウィック',
    'Wukong': 'ウーコン',
    'Xayah': 'ゼヤ',
    'Xin Zhao': 'シン・ジャオ',
    'Yasuo': 'ヤスオ',
    'Yone': 'ヨネ',
    'Yuumi': 'ユミ',
    'Zeri': 'ゼリ',
    'Zed': 'ゼド',
    'Ziggs': 'ズィグス',
    'Zoe': 'ゾーイ',
    'Zyra': 'ズヤ'
}

# Counter data from the user's input
counter_data = {
    'Aatrox': ['Irelia', 'Darius', 'Ornn', 'Jax', 'Yasuo', 'Malphite', 'Vayne'],
    'Ahri': ['Yasuo', 'Ekko', 'Diana', 'Irelia', 'Kassadin', 'Galio'],
    'Akali': ['Kassadin', 'Galio', 'Annie', 'Veigar', 'Akshan', 'Vex', 'Twisted Fate'],
    'Akshan': ['Yasuo', 'Irelia', 'Lissandra', 'Veigar', 'Zed', 'Fizz'],
    'Alistar': ['Janna', 'Morgana', 'Thresh', 'Zyra', 'Lulu', 'Rakan'],
    'Ambessa (Top)': ['Pantheon', 'Jayce', 'Darius', 'Garen', 'Singed'],
    'Ambessa (Jg)': ['Shyvana', 'Kha\'Zix', 'Wukong', 'Viego', 'Fiddlesticks', 'Warwick'],
    'Amumu': ['Shyvana', 'Lee Sin', 'Vi', 'Warwick', 'Kha\'Zix', 'Volibear', 'Olaf'],
    'Annie': ['Kassadin', 'Brand', 'Orianna', 'Fizz', 'Veigar', 'Lux'],
    'Ashe': ['Caitlyn', 'Draven', 'Jhin', 'Tristana', 'Ezreal', 'Lucian'],
    'Aurelion Sol': ['Fizz', 'Zed', 'Yasuo', 'Lux', 'Katarina', 'Karma', 'Galio', 'Zyra'],
    'Blitzcrank': ['Leona', 'Alistar', 'Morgana', 'Thresh', 'Braum', 'Rakan', 'Zyra'],
    'Brand (Mid)': ['Fizz', 'Galio', 'Lux', 'Zed', 'Corki', 'Ekko'],
    'Brand (Sup)': ['Maokai', 'Pyke', 'Nautilus', 'Blitzcrank', 'Morgana', 'Braum'],
    'Braum': ['Morgana', 'Leona', 'Soraka', 'Alistar', 'Karma', 'Vayne', 'Senna'],
    'Caitlyn': ['Jhin', 'Ezreal', 'Nilah', 'Twitch', 'Jinx', 'Draven'],
    'Camille': ['Renekton', 'Darius', 'Fiora', 'Riven', 'Nasus', 'Shen'],
    'Corki (Mid)': ['Zed', 'Fizz', 'Lux', 'Ahri', 'Brand', 'Syndra'],
    'Corki (Adc)': ['Caitlyn', 'Draven', 'Ashe', 'Varus', 'Lucian', 'Sivir'],
    'Darius (Top)': ['Vayne', 'Ornn', 'Kayle', 'Jayce', 'Urgot'],
    'Darius (Jg)': ['Wukong', 'Nunu', 'Master Yi', 'Ekko', 'Evelynn', 'Viego'],
    'Diana (Mid)': ['Kayle', 'Fizz', 'Pantheon', 'Gragas', 'Ekko', 'Jayce'],
    'Diana (Jg)': ['Fizz', 'Jax', 'Pantheon', 'Tryndamere', 'Kayle', 'Ekko'],
    'Dr. Mundo (Top)': ['Darius', 'Aatrox', 'Vayne', 'Gwen', 'Fiora', 'Camille', 'Gragas'],
    'Dr. Mundo (Jg)': ['Gragas', 'Xin Zhao', 'Kayn', 'Viego', 'Lillia', 'Ekko'],
    'Draven': ['Senna', 'Jhin', 'Ashe', 'Nilah', 'Ziggs'],
    'Ekko (Mid)': ['Kassadin', 'Galio', 'Swain', 'Irelia', 'Yasuo', 'Akali'],
    'Ekko (Jg)': ['Kha\'Zix', 'Rengar', 'Amumu', 'Vi', 'Nunu', 'Talon'],
    'Evelynn': ['Kha\'Zix', 'Xin Zhao', 'Lee Sin', 'Master Yi', 'Rengar', 'Fiddlesticks'],
    'Ezreal': ['Nilah', 'Vayne', 'Draven', 'Tristana', 'Kalista'],
    'Fiddlesticks': ['Shyvana', 'Vi', 'Amumu', 'Ekko', 'Xin Zhao', 'Dr. Mundo'],
    'Fiora': ['Warwick', 'Vayne', 'Pantheon', 'Darius', 'Renekton', 'Malphite'],
    'Fizz (Mid)': ['Diana', 'Gragas', 'Kassadin', 'Akali', 'Kayle', 'Annie'],
    'Fizz (Jg)': ['Kayn', 'Evelynn', 'Vi', 'Warwick', 'Kha\'Zix', 'Master Yi'],
    'Galio (Mid)': ['Yasuo', 'Swain', 'Orianna', 'Ahri', 'Vex', 'Syndra'],
    'Galio (Sup)': ['Alistar', 'Lulu', 'Janna', 'Braum', 'Zyra', 'Lux'],
    'Garen': ['Darius', 'Camille', 'Kayle', 'Fiora', 'Shen', 'Ornn', 'Vayne'],
    'Gnar': ['Irelia', 'Darius', 'Olaf', 'Renekton', 'Nasus', 'Camille'],
    'Gragas (Top)': ['Pantheon', 'Aatrox', 'Jax', 'Darius', 'Kennen', 'Garen'],
    'Gragas (Jg)': ['Lee Sin', 'Rengar', 'Kha\'Zix', 'Viego', 'Evelynn', 'Diana'],
    'Graves': ['Evelynn', 'Vi', 'Rengar', 'Kha\'Zix', 'Rammus', 'Fiddlesticks'],
    'Gwen': ['Fiora', 'Jax', 'Riven', 'Darius', 'Nasus', 'Tryndamere'],
    'Hecarim': ['Master Yi', 'Evelynn', 'Warwick', 'Vi', 'Jarvan IV', 'Graves'],
    'Heimerdinger': ['Zoe', 'Veigar', 'Ekko', 'Syndra', 'Lux', 'Zed'],
    'Irelia (Mid)': ['Ekko', 'Zoe', 'Vex', 'Annie', 'Yasuo', 'Syndra'],
    'Irelia (Top)': ['Garen', 'Darius', 'Renekton', 'Malphite', 'Nasus', 'Sett'],
    'Janna': ['Nami', 'Blitzcrank', 'Lux', 'Sona', 'Soraka', 'Senna'],
    'Jarvan IV': ['Vi', 'Lee Sin', 'Xin Zhao', 'Nunu', 'Ekko', 'Gwen'],
    'Jax (Top)': ['Renekton', 'Garen', 'Pantheon', 'Urgot', 'Dr. Mundo', 'Singed', 'Gragas'],
    'Jax (Jg)': ['Kha\'Zix', 'Kayn', 'Rammus', 'Fiddlesticks', 'Evelynn', 'Lillia'],
    'Jayce (Mid)': ['Brand', 'Annie', 'Galio', 'Zoe', 'Diana', 'Vex'],
    'Jayce (Top)': ['Olaf', 'Renekton', 'Fiora', 'Wukong', 'Pantheon', 'Urgot'],
    'Jhin': ['Lucian', 'Vayne', 'Tristana', 'Nilah', 'Twitch', 'Jinx'],
    'Jinx': ['Draven', 'Tristana', 'Xayah', 'Twitch', 'Nilah', 'Senna'],
    'Kai\'Sa': ['Vayne', 'Xayah', 'Ezreal', 'Sivir', 'Lucian', 'Caitlyn'],
    'Kalista': ['Nilah', 'Xayah', 'Lucian', 'Twitch', 'Ashe', 'Zeri'],
    'Karma (Sup)': ['Sona', 'Lulu', 'Blitzcrank', 'Zyra', 'Rakan', 'Morgana'],
    'Karma (Mid)': ['Veigar', 'Lux', 'Orianna', 'Ahri', 'Yasuo', 'Ekko'],
    'Kassadin': ['Zed', 'Yasuo', 'Riven', 'Yone', 'Ekko', 'Jayce'],
    'Katarina': ['Fizz', 'Kayle', 'Yasuo', 'Pantheon', 'Annie', 'Ahri', 'Galio'],
    'Kayle (Top)': ['Pantheon', 'Riven', 'Jax', 'Wukong', 'Jayce', 'Yone'],
    'Kayle (Mid)': ['Annie', 'Orianna', 'Ziggs', 'Syndra', 'Zoe', 'Twisted Fate'],
    'Kayn': ['Vi', 'Rengar', 'Shyvana', 'Evelynn', 'Master Yi', 'Xin Zhao'],
    'Kennen (Top)': ['Nasus', 'Irelia', 'Dr. Mundo', 'Olaf', 'Vladimir', 'Kayle'],
    'Kennen (Mid)': ['Diana', 'Ahri', 'Vladimir', 'Annie', 'Galio', 'Brand'],
    'Kha\'Zix': ['Rengar', 'Vi', 'Lee Sin', 'Volibear', 'Warwick', 'Rammus'],
    'Kindred': ['Lee Sin', 'Gragas', 'Master Yi', 'Evelynn', 'Kha\'Zix', 'Vi'],
    'Lee Sin': ['Rammus', 'Wukong', 'Fiddlesticks', 'Warwick', 'Graves'],
    'Leona': ['Morgana', 'Alistar', 'Janna', 'Karma', 'Braum', 'Thresh'],
    'Lillia': ['Rengar', 'Ekko', 'Diana', 'Master Yi', 'Evelynn', 'Jarvan IV'],
    'Lissandra': ['Vex', 'Lux', 'Malphite', 'Kassadin', 'Varus', 'Galio'],
    'Lucian (Adc)': ['Vayne', 'Ashe', 'Nilah', 'Caitlyn', 'Twitch', 'Tristana'],
    'Lucian (Mid)': ['Brand', 'Galio', 'Annie', 'Aurelion Sol', 'Fizz', 'Yasuo'],
    'Lulu': ['Sona', 'Soraka', 'Blitzcrank', 'Rakan', 'Karma', 'Leona'],
    'Lux (Mid)': ['Fizz', 'Kassadin', 'Ahri', 'Yasuo', 'Karma', 'Yone'],
    'Lux (Sup)': ['Sona', 'Blitzcrank', 'Soraka', 'Nautilus', 'Zyra', 'Leona'],
    'Master Yi': ['Rammus', 'Vi', 'Amumu', 'Kha\'Zix', 'Warwick', 'Kayn'],
    'Malphite (Top)': ['Fiora', 'Olaf', 'Darius', 'Garen', 'Shen', 'Dr. Mundo'],
    'Malphite (Mid)': ['Diana', 'Annie', 'Morgana', 'Fizz', 'Ekko', 'Kassadin'],
    'Malphite (Sup)': ['Morgana', 'Sona', 'Senna', 'Rakan', 'Thresh', 'Nautilus'],
    'Maokai (Sup)': ['Braum', 'Alistar', 'Janna', 'Thresh', 'Lulu', 'Zyra'],
    'Maokai (Jg)': ['Rammus', 'Warwick', 'Jarvan IV', 'Nunu', 'Rengar', 'Lillia'],
    'Maokai (Top)': ['Garen', 'Dr. Mundo', 'Nasus', 'Sett', 'Camille', 'Fiora'],
    'Milio': ['Blitzcrank', 'Thresh', 'Pyke', 'Nautilus', 'Senna', 'Lux'],
    'Miss Fortune': ['Tristana', 'Draven', 'Caitlyn', 'Lucian', 'Senna', 'Vayne'],
    'Mordekaiser (Top)': ['Olaf', 'Fiora', 'Warwick', 'Riven', 'Jax', 'Gwen'],
    'Mordekaiser (Jg)': ['Master Yi', 'Warwick', 'Lillia', 'Ekko', 'Pantheon', 'Gragas'],
    'Morgana (Sup)': ['Karma', 'Janna', 'Sona', 'Soraka', 'Yuumi', 'Lulu'],
    'Morgana (Mid)': ['Fizz', 'Zed', 'Katarina', 'Seraphine', 'Tristana', 'Lissandra'],
    'Morgana (Jg)': ['Zed', 'Fizz', 'Olaf', 'Amumu', 'Rengar', 'Ambessa'],
    'Nami': ['Lulu', 'Blitzcrank', 'Morgana', 'Leona', 'Alistar', 'Sona'],
    'Nasus': ['Darius', 'Teemo', 'Pantheon', 'Volibear', 'Olaf', 'Garen', 'Camille', 'Gwen'],
    'Nautilus': ['Morgana', 'Janna', 'Alistar', 'Rakan', 'Seraphine', 'Lulu'],
    'Nilah (Jg)': ['Rammus', 'Vi', 'Amumu', 'Ambessa', 'Fiddlesticks', 'Evelynn'],
    'Nilah (Adc)': ['Caitlyn', 'Xayah', 'Sivir', 'Draven', 'Jinx', 'Ashe'],
    'Nunu': ['Lee Sin', 'Vi', 'Kha\'Zix', 'Diana', 'Evelynn', 'Gragas'],
    'Olaf (Jg)': ['Gragas', 'Jarvan IV', 'Warwick', 'Rengar', 'Fiddlesticks', 'Master Yi'],
    'Olaf (Top)': ['Volibear', 'Jax', 'Kayle', 'Sett', 'Riven'],
    'Orianna': ['Diana', 'Gragas', 'Ziggs', 'Ahri', 'Zed', 'Syndra'],
    'Ornn': ['Fiora', 'Shen', 'Olaf', 'Camille', 'Vayne', 'Gwen'],
    'Pantheon (Jg)': ['Rammus', 'Vi', 'Diana', 'Rengar', 'Shyvana', 'Dr. Mundo'],
    'Pantheon (Top)': ['Fiora', 'Malphite', 'Camille', 'Olaf', 'Shen', 'Jayce'],
    'Pantheon (Mid)': ['Orianna', 'Ahri', 'Zoe', 'Syndra', 'Jayce', 'Swain'],
    'Pyke': ['Leona', 'Nautilus', 'Rakan', 'Blitzcrank', 'Maokai', 'Braum'],
    'Rakan': ['Lulu', 'Leona', 'Janna', 'Alistar', 'Karma', 'Milio'],
    'Rammus': ['Fiddlesticks', 'Evelynn', 'Lillia', 'Amumu', 'Nunu', 'Shyvana'],
    'Renekton': ['Vayne', 'Garen', 'Olaf', 'Kayle', 'Teemo', 'Pantheon'],
    'Rengar': ['Rammus', 'Amumu', 'Jarvan IV', 'Warwick', 'Master Yi', 'Vi'],
    'Riven': ['Ornn', 'Shen', 'Sett', 'Urgot', 'Renekton', 'Garen'],
    'Rumble': ['Garen', 'Jayce', 'Sion', 'Shen', 'Camille', 'Tryndamere'],
    'Samira': ['Draven', 'Miss Fortune', 'Senna', 'Nilah', 'Jinx', 'Xayah'],
    'Senna (Sup)': ['Blitzcrank', 'Rakan', 'Leona', 'Thresh', 'Braum', 'Nautilus'],
    'Senna (Adc)': ['Caitlyn', 'Jhin', 'Ezreal', 'Kalista', 'Lucian', 'Vayne'],
    'Seraphine (Sup)': ['Sona', 'Soraka', 'Janna', 'Senna', 'Pyke', 'Milio'],
    'Seraphine (Mid)': ['Fizz', 'Ziggs', 'Irelia', 'Katarina', 'Kayle', 'Zed'],
    'Sett': ['Malphite', 'Renekton', 'Garen', 'Pantheon', 'Singed', 'Volibear'],
    'Shyvana': ['Vi', 'Lee Sin', 'Kha\'Zix', 'Gragas', 'Volibear', 'Gwen'],
    'Singed': ['Kennen', 'Riven', 'Fiora', 'Urgot', 'Warwick', 'Darius'],
    'Sion (Top)': ['Pantheon', 'Aatrox', 'Garen', 'Nasus', 'Darius', 'Riven', 'Jax'],
    'Sion (Jg)': ['Warwick', 'Ambessa', 'Gwen', 'Vi', 'Kindred'],
    'Sivir': ['Jhin', 'Jinx', 'Kai\'Sa', 'Miss Fortune', 'Ashe'],
    'Sona': ['Blitzcrank', 'Leona', 'Thresh', 'Nautilus', 'Zyra', 'Alistar'],
    'Soraka': ['Blitzcrank', 'Thresh', 'Leona', 'Pyke', 'Nautilus', 'Alistar'],
    'Swain (Mid)': ['Ahri', 'Jayce', 'Akshan', 'Fizz', 'Yone', 'Galio'],
    'Swain (Sup)': ['Brand', 'Lux', 'Lulu', 'Morgana', 'Janna', 'Zyra'],
    'Syndra': ['Kassadin', 'Fizz', 'Lux', 'Yasuo', 'Kayle', 'Talon'],
    'Talon (Mid)': ['Ekko', 'Vex', 'Veigar', 'Fizz', 'Kassadin', 'Katarina'],
    'Talon (Jg)': ['Rammus', 'Xin Zhao', 'Amumu', 'Diana', 'Fiddlesticks', 'Vi'],
    'Teemo (Top)': ['Pantheon', 'Jayce', 'Ornn', 'Malphite', 'Riven', 'Irelia'],
    'Teemo (Mid)': ['Fizz', 'Lux', 'Karma', 'Galio', 'Zoe', 'Vex'],
    'Thresh': ['Lulu', 'Morgana', 'Janna', 'Nami', 'Zyra', 'Seraphine'],
    'Tristana': ['Draven', 'Sivir', 'Lucian', 'Jinx', 'Caitlyn', 'Nilah'],
    'Tryndamere (Top)': ['Malphite', 'Teemo', 'Darius', 'Renekton', 'Sett'],
    'Tryndamere (Jg)': ['Fizz', 'Kayle', 'Ekko', 'Gragas', 'Warwick'],
    'Twisted Fate': ['Fizz', 'Diana', 'Ahri', 'Yasuo', 'Veigar', 'Zed'],
    'Twitch (Adc)': ['Jhin', 'Tristana', 'Kai\'Sa', 'Draven', 'Xayah', 'Samira'],
    'Twitch (Jg)': ['Vi', 'Kha\'Zix', 'Rengar', 'Evelynn', 'Lee Sin', 'Kayn'],
    'Urgot': ['Dr. Mundo', 'Kayle', 'Teemo', 'Olaf', 'Garen', 'Ornn'],
    'Varus (Adc)': ['Twitch', 'Jinx', 'Miss Fortune', 'Sivir', 'Samira', 'Jhin'],
    'Varus (Mid)': ['Annie', 'Zoe', 'Jayce', 'Yasuo', 'Katarina', 'Yone'],
    'Vayne (Adc)': ['Caitlyn', 'Draven', 'Varus', 'Ashe', 'Tristana', 'Nilah'],
    'Vayne (Top)': ['Pantheon', 'Teemo', 'Malphite', 'Yone', 'Jayce', 'Vladimir'],
    'Veigar': ['Zed', 'Katarina', 'Diana', 'Zoe', 'Jayce', 'Ekko'],
    'Vex': ['Pantheon', 'Galio', 'Veigar', 'Kassadin', 'Katarina', 'Kayle'],
    'Vi': ['Lee Sin', 'Xin Zhao', 'Warwick', 'Diana', 'Volibear', 'Olaf'],
    'Viego': ['Rammus', 'Evelynn', 'Warwick', 'Vi', 'Ekko', 'Amumu'],
    'Viktor': ['Ekko', 'Fizz', 'Zed', 'Kassadin', 'Yasuo', 'Akali'],
    'Vladimir (Mid)': ['Fizz', 'Kassadin', 'Ahri', 'Orianna', 'Ziggs'],
    'Vladimir (Top)': ['Kennen', 'Camille', 'Irelia', 'Riven', 'Darius', 'Yone', 'Nasus', 'Aatrox'],
    'Volibear (Top)': ['Jayce', 'Vayne', 'Teemo', 'Fiora', 'Darius', 'Kayle'],
    'Volibear (Jg)': ['Wukong', 'Master Yi', 'Amumu', 'Rengar', 'Lillia', 'Fiddlesticks'],
    'Warwick (Jg)': ['Evelynn', 'Nunu', 'Rengar', 'Maokai', 'Rammus', 'Vi'],
    'Warwick (Top)': ['Kayle', 'Olaf', 'Urgot', 'Singed', 'Darius', 'Nasus'],
    'Wukong (Jg)': ['Lee Sin', 'Amumu', 'Jarvan IV', 'Evelynn', 'Vi', 'Shyvana'],
    'Wukong (Top)': ['Ornn', 'Darius', 'Garen', 'Nasus', 'Olaf', 'Volibear'],
    'Xayah': ['Miss Fortune', 'Tristana', 'Varus', 'Caitlyn', 'Draven'],
    'Xin Zhao': ['Malphite', 'Rammus', 'Lee Sin', 'Evelynn', 'Ekko', 'Master Yi'],
    'Yasuo (Mid)': ['Fizz', 'Renekton', 'Annie', 'Vex', 'Vladimir', 'Swain'],
    'Yasuo (Top)': ['Renekton', 'Nasus', 'Tryndamere', 'Garen', 'Camille', 'Darius'],
    'Yone (Top)': ['Pantheon', 'Urgot', 'Riven', 'Fiora', 'Garen', 'Sett'],
    'Yone (Mid)': ['Annie', 'Zed', 'Fizz', 'Ahri', 'Veigar', 'Talon'],
    'Yuumi': ['Leona', 'Alistar', 'Rakan', 'Blitzcrank', 'Soraka', 'Sona'],
    'Zeri': ['Draven', 'Tristana', 'Jhin', 'Caitlyn', 'Vayne', 'Samira'],
    'Zed (Mid)': ['Fizz', 'Ekko', 'Vladimir', 'Ahri', 'Kayle', 'Galio'],
    'Zed (Jg)': ['Rammus', 'Amumu', 'Kindred', 'Rengar', 'Kayn', 'Master Yi'],
    'Ziggs': ['Kayle', 'Talon', 'Brand', 'Ekko', 'Annie', 'Garen'],
    'Zoe': ['Veigar', 'Ahri', 'Kassadin', 'Twisted Fate', 'Akali', 'Zed'],
    'Zyra (Sup)': ['Janna', 'Sona', 'Thresh', 'Morgana', 'Alistar', 'Soraka'],
    'Zyra (Mid)': ['Ziggs', 'Heimerdinger', 'Lux', 'Syndra', 'Katarina', 'Zed']
}

def get_champion_image_url(champion_name):
    """Get Data Dragon image URL for champion"""
    # Handle special cases for champion names
    image_mapping = {
        'Kha\'Zix': 'Khazix',
        'Kai\'Sa': 'Kaisa',
        'Master Yi': 'MasterYi',
        'Jarvan IV': 'JarvanIV',
        'Lee Sin': 'LeeSin',
        'Xin Zhao': 'XinZhao',
        'Twisted Fate': 'TwistedFate',
        'Miss Fortune': 'MissFortune',
        'Dr. Mundo': 'DrMundo',
        'Aurelion Sol': 'AurelionSol',
        'Master Yi': 'MasterYi'
    }
    
    image_name = image_mapping.get(champion_name, champion_name)
    return f"https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/{image_name}.png"

def generate_champion_html(champion_key, counters):
    """Generate HTML for a champion with counters"""
    # Determine lane based on champion name
    lane = 'all'
    if '(Top)' in champion_key:
        lane = 'top'
    elif '(Jg)' in champion_key or '(Jungle)' in champion_key:
        lane = 'jungle'
    elif '(Mid)' in champion_key:
        lane = 'mid'
    elif '(Adc)' in champion_key or '(ADC)' in champion_key:
        lane = 'adc'
    elif '(Sup)' in champion_key or '(Support)' in champion_key:
        lane = 'support'
    
    # Clean champion name for display and mapping
    clean_name = champion_key.replace('(Top)', '').replace('(Jg)', '').replace('(Mid)', '').replace('(Adc)', '').replace('(Sup)', '').replace('(Jungle)', '').replace('(ADC)', '').replace('(Support)', '').strip()
    
    # Handle special cases
    if clean_name == 'Ambessa':
        clean_name = 'Amumu'  # Ambessa is Amumu in Japanese
    
    champion_name_jp = champion_mapping.get(clean_name, clean_name)
    image_url = get_champion_image_url(clean_name)
    
    html = f'''            <div class="champion-item" data-champion="{champion_name_jp}" data-lanes="{lane}">
                <h3><img src="{image_url}" width="32" height="32" alt="{champion_name_jp}"> {champion_name_jp}</h3>
                <ul>
                    <li><b>カウンター:</b> '''
    
    counter_images = []
    for counter in counters:
        counter_jp = champion_mapping.get(counter, counter)
        counter_image_url = get_champion_image_url(counter)
        counter_images.append(f'<img src="{counter_image_url}" width="24" height="24" alt="{counter_jp}"> {counter_jp}')
    
    html += ', '.join(counter_images)
    html += '</li>\n                </ul>\n            </div>\n\n'
    
    return html

# Generate HTML for all champions
html_content = '''        <div class="champion-section" data-lane="all">
            <h2>WR - 各チャンピオンのカウンターリスト！</h2>
            
'''

for champion_key, counters in counter_data.items():
    html_content += generate_champion_html(champion_key, counters)

html_content += '        </div>\n'

print(html_content)
