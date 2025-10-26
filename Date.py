from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64

# Chromeドライバーのパスを指定
service = Service('C:\\Practice\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service)

# ウェブサイトを開く
driver.get('https://input.vlog.jp/users/sign_in')  # ログインURL
print("ログインページを開きました。")

# ログイン情報を入力
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'user_email')))
    driver.find_element(By.ID, 'user_email').send_keys('nvk1n@vlog.jp')  # ログインID
    driver.find_element(By.ID, 'user_password').send_keys('xXyYNinF')  # パスワード
    print("ログイン情報を入力しました。")

    # ログインボタンをクリック
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()  # ログインボタンのXPath
    print("ログインボタンをクリックしました。")

    # ページが読み込まれるのを待つ
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="image_id"]')))
    print("画像が表示されるのを待っています。")
    
    # 画像を取得
    try:
        image_element = driver.find_element(By.XPATH, '//*[@id="image_id"]')  # 正しいXPathに置き換え
        image_src = image_element.get_attribute('src')  # src属性からBase64データを取得
        print("画像のBase64データを取得しました。")

        # Base64データをデコードして保存
        if image_src.startswith("data:image/png;base64,"):
            base64_data = image_src.split(",")[1]  # Base64部分を取得
            image_data = base64.b64decode(base64_data)  # デコード

            # 画像を保存
            with open('C:\\Practice\\img\\screenshot.png', 'wb') as file:
                file.write(image_data)
            print("画像をC:\\Practice\\imgに保存しました。")
        else:
            print("画像データがBase64形式ではありません。")

    except Exception as e:
        print("画像の取得中にエラーが発生しました:", e)

except Exception as e:
    print("エラーが発生しました:", e)

# 終了処理
# driver.quit()  # スクリプトの実行が完了した後に手動でウィンドウを閉じる