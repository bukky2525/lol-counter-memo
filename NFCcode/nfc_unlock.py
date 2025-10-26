import tkinter as tk
import subprocess
import nfc
import threading

# ロックをかけるフォルダのパス
folder_to_lock = r"D:\H"

# フォルダのロックを解除する関数
def unlock_folder():
    # 'Everyone'のアクセス権を解除するコマンド
    result = subprocess.run(
        f'icacls "{folder_to_lock}" /remove Everyone',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        status_label.config(text=f"フォルダのロックが解除されました。")
    else:
        status_label.config(text=f"エラー: フォルダのロック解除に失敗しました。")

# NFCリーダーからUIDを取得する関数
def on_connect(tag):
    tag_uid = tag.identifier.hex().upper()

    if tag_uid == "042159AF722681":
        status_label.config(text="UIDが認識されました。ロックを解除します。")
        unlock_folder()
    else:
        status_label.config(text="指定されたUIDではないため、ロックを解除しません。")

    return True

# NFCタグを読み取る関数
def read_nfc_tag():
    # NFCリーダーを設定し、接続を待つ
    clf = nfc.ContactlessFrontend('usb')
    clf.connect(rdwr={'on-connect': on_connect})

    # 1秒後にアプリを閉じる
    root.after(1000, root.quit)

# スレッドでNFCタグの読み取りを開始する関数
def start_reading():
    threading.Thread(target=read_nfc_tag).start()

# ウィンドウが閉じられるときの処理
def on_closing():
    root.quit()

# GUIの設定
root = tk.Tk()
root.title("ロック解除アプリ")

root.geometry("300x200")

# 初期メッセージを表示
uid_label = tk.Label(root, text="NFCを読み取らせてください")
uid_label.pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack(pady=10)

# ボタンが押されたときにNFCタグの読み取りを開始
read_button = tk.Button(root, text="NFCタグを読み取る", command=start_reading)
read_button.pack(pady=20)

# ウィンドウの×ボタンが押されたときの処理を設定
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
