import nfc
import sqlite3
import time
import os
import subprocess

LOCK_FILE = '/tmp/locked_state.txt'  # ロック状態を保存するファイル

# ロック状態を取得する関数
def get_lock_state():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, 'r') as f:
            return f.read().strip() == 'locked'
    return True  # デフォルトはロックされている状態

# ロック状態を更新する関数
def set_lock_state(locked):
    with open(LOCK_FILE, 'w') as f:
        f.write('locked' if locked else 'unlocked')

# UIDに対応する名前をデータベースから取得する関数
def get_name_from_db(uid):
    conn = sqlite3.connect('cards.db', timeout=10)
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM cards WHERE uid = ?', (uid,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None

# UIDに対応する名前をデータベースに保存する関数
def save_name_to_db(uid, name):
    conn = sqlite3.connect('cards.db', timeout=10)
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO cards (uid, name) VALUES (?, ?)', (uid, name))
        conn.commit()
        print(f"新しいカード {uid} に名前 '{name}' を登録しました")
    except sqlite3.OperationalError as e:
        print(f"データベースロックエラーが発生しました: {e}")
        time.sleep(1)
        save_name_to_db(uid, name)  # 再試行
    finally:
        conn.close()

# UIDに対応する名前を更新する関数
def update_name_in_db(uid, new_name):
    conn = sqlite3.connect('cards.db', timeout=10)
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE cards SET name = ? WHERE uid = ?', (new_name, uid))
        conn.commit()
        print(f"カード {uid} の名前が '{new_name}' に更新されました")
    except sqlite3.OperationalError as e:
        print(f"データベースロックエラーが発生しました: {e}")
        time.sleep(1)
        update_name_in_db(uid, new_name)  # 再試行
    finally:
        conn.close()

# ロック解除処理
def unlock_system():
    # ロック状態を解除する
    print("ロック解除されました。")
    set_lock_state(False)
    # ここでPCのロック解除の実行を行うことができます。
    subprocess.run("gnome-screensaver-command -d", shell=True)  # GNOMEの場合、画面ロック解除コマンド

# カードが接続されたときに呼ばれるコールバック関数
def on_connect(tag):
    uid = tag.identifier.hex().upper()
    print(f"カードのUID: {uid}")

    # ロック状態が解除されているか確認
    if get_lock_state():
        # データベースから名前を取得
        name = get_name_from_db(uid)

        if name:
            print(f"カードの名前: {name}")
            # 名前を変更するかどうかを尋ねる
            change_name = input("名前を変更しますか？ (y/n): ").strip().lower()
            if change_name == 'y':
                new_name = input("新しい名前を入力してください: ")
                update_name_in_db(uid, new_name)
        else:
            # 新しいカードの場合、名前を入力してデータベースに保存
            print("新しいカードです！")
            new_name = input(f"カード {uid} に名前をつけてください: ")
            save_name_to_db(uid, new_name)
            print(f"カード {uid} の名前が '{new_name}' に設定されました")

        # ロック解除
        unlock_system()
    else:
        print("システムはロックされています。カードを認識しましたが、ロック解除はできません。")
    return True

# NFCリーダーの接続
with nfc.ContactlessFrontend('usb') as clf:
    print("💳 NTAGカードをかざしてください...")
    clf.connect(rdwr={'on-connect': on_connect})

