import sqlite3

# SQLiteデータベースの接続（ファイル名を指定）
# ファイルが存在しない場合は新しく作成されます
def create_database():
    conn = sqlite3.connect('cards.db')
    cursor = conn.cursor()
    
    # カードのUIDと名前を格納するテーブルを作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards (
        uid TEXT PRIMARY KEY,
        name TEXT
    )
    ''')

    conn.commit()  # コミットしてデータベースの変更を確定
    conn.close()  # 接続を閉じる
    print("データベースとテーブルが作成されました。")

# カードのUIDと名前をデータベースに保存する関数
def save_name_to_db(uid, name):
    conn = sqlite3.connect('cards.db')  # データベースに接続
    cursor = conn.cursor()  # カーソルを作成

    # カードのUIDと名前を挿入または更新
    cursor.execute('''
    INSERT OR REPLACE INTO cards (uid, name) VALUES (?, ?)
    ''', (uid, name))  # プレースホルダーを使ってSQLインジェクションを防止

    conn.commit()  # コミットしてデータベースの変更を確定
    conn.close()  # 接続を閉じる

    print(f"カード {uid} に名前 '{name}' を保存しました。")

# UIDに対応する名前をデータベースから取得する関数
def get_name_from_db(uid):
    conn = sqlite3.connect('cards.db')  # データベースに接続
    cursor = conn.cursor()  # カーソルを作成

    cursor.execute('SELECT name FROM cards WHERE uid = ?', (uid,))
    result = cursor.fetchone()  # 結果を1件だけ取得

    conn.close()  # 接続を閉じる

    if result:
        return result[0]  # 名前を返す
    else:
        return None  # 名前が見つからなければNoneを返す

# データベース内のすべてのカード情報を表示する関数
def list_all_cards():
    conn = sqlite3.connect('cards.db')  # データベースに接続
    cursor = conn.cursor()  # カーソルを作成

    cursor.execute('SELECT uid, name FROM cards')
    cards = cursor.fetchall()  # すべてのカードを取得

    conn.close()  # 接続を閉じる

    if cards:
        print("データベース内のすべてのカード情報:")
        for card in cards:
            print(f"UID: {card[0]}, 名前: {card[1]}")
    else:
        print("データベースに保存されているカードはありません。")

# 実際に使う例
def main():
    # データベースとテーブルの作成
    create_database()

    # カードのUIDと名前を登録
    save_name_to_db("1234567890", "Alice")
    save_name_to_db("0987654321", "Bob")

    # 名前を取得
    name = get_name_from_db("1234567890")
    print(f"カード '1234567890' の名前は: {name}")

    # すべてのカード情報を表示
    list_all_cards()

if __name__ == '__main__':
    main()
