import subprocess

# ロックするフォルダのパス
folder_to_lock = r"ロックしたいフォルダの指定"  #ロックしたいフォルダを指定

# フォルダにロックをかける関数
def lock_folder():
    result = subprocess.run(
        f'icacls "{folder_to_lock}" /deny Everyone:(OI)(CI)F',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"フォルダ {folder_to_lock} にロックがかかりました。")
    else:
        print(f"エラー: フォルダ {folder_to_lock} のロックに失敗しました。")
        print(f"エラーメッセージ: {result.stderr}")

# フォルダがロックされていない場合、ロックをかける
lock_folder()
