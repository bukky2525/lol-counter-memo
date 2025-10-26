import subprocess

# ロックをかけるフォルダのパス
folder_to_lock = r"D:\H"

# フォルダにロックをかける関数
def lock_folder():
    # 'Everyone'に対してアクセス権を拒否するコマンド
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

if __name__ == '__main__':
    # フォルダがロックされていない場合、ロックをかける
    lock_folder()
