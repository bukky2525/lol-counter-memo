import os
import pickle
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from flask import Flask, render_template, request, redirect, url_for

# Flaskのインスタンスを作成
app = Flask(__name__)

# 認証情報のスコープ (メール送信に必要なスコープ)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# トークンの保存先
CREDENTIALS_PATH = './.vscode/credentials.json'  # ファイルのパス
TOKEN_PICKLE_PATH = 'token.pickle'

def authenticate_gmail():
    """Googleアカウントで認証してトークンを取得"""
    creds = None
    # トークンが保存されている場合はそれをロードする
    if os.path.exists(TOKEN_PICKLE_PATH):
        with open(TOKEN_PICKLE_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # トークンが無効か期限切れの場合は再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 認証が成功した場合、トークンを保存
        with open(TOKEN_PICKLE_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def send_email_with_gmail():
    """Gmail APIを使ってメールを送信"""
    try:
        creds = authenticate_gmail()  # 認証

        # Gmail APIのサービスを作成
        service = build('gmail', 'v1', credentials=creds)

        # メールの作成
        message = MIMEMultipart()
        message['to'] = to_email  # 送信先メールアドレス
        message['subject'] = 'Test Email'

        # 本文
        body = 'This is a test email sent using Gmail API.'
        message.attach(MIMEText(body, 'plain'))

        # メール送信のためにbase64エンコード
        raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        # Gmail APIを使ってメッセージを送信
        send_message = service.users().messages().send(userId="me", body=raw_message).execute()
        
        print(f'Email sent! Message ID: {send_message["id"]}')
    except Exception as error:
        print(f'An error occurred: {error}')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.methods == 'POST':
        to_email = request.form['email'] #フォームから入力されたメールアドレス
        send_email_with_gmail(to_email)  #メール送信
        return redirect(url_for('success'))
    return render_template('index.html')

@app.route('/seccess')
def succes():
    return 'Email sent successfully!'

if __name__ == '__main__':
    send_email_with_gmail()
    
