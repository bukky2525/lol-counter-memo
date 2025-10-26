#GUIライブラリの読み込み
#tkinterのインポート
import tkinter as tk
from tkinter import messagebox

'''
商品リスト（名前：値段）
キー(商品名): 値(価格)
productsは辞書型(dict)
'''
products = {
    'ハンバーガー': 300,
    'ポテト': 200,
    'コーラ': 150,
    'ナゲット': 400
}

'''
カート（注文リスト）
注文された商品の名前をキーにして、購入数を値として保存する
cartは辞書型(dict)
'''
cart = {}

'''商品をカートに追加する関数'''
def add_to_cart(product_name):
    if product_name in cart:
        cart[product_name] += 1     #すでにカートにある商品なら、個数+1
    else:
        cart[product_name] = 1      #初めて追加する商品なら、1個目として登録
    update_cart_display()   #カートの表示を更新

'''カートの内容更新'''
def update_cart_display():
    cart_text.delete(1.0, tk.END) #テキストボックスの内容をクリア
    total_price = 0     #合計金額の初期化

    for procut, quantity in cart.items():   #カートの中の商品を1つずつ取り出す
        price = products[product] * quantity    #商品の数　＊　個数
        cart_text.insert(tk.END, f'{procut} x {quantity} = {price}円\n')    #テキストエリアに表示
        total_price += price    #合計金額を計算

    cart_text.insert(tk.END, f'\n合計: {total_price}円')    #最後に合計金額を表示
    
'''注文を確定する関数'''
def confirm_oder():
    if not cart:
        messagebox.showwarning('警告', 'カートが空です！')      #カートが空なら警告
        return
    
    messagebox.showinfo('注文確定', 'ご注文ありがとうございます！')     #注文確定のポップアップ
    cart.clear()    #カートを空にする
    update_cart_display()   #画面の表示を個数

#メインウィンドウ
root = tk.Tk()  #アプリのウィンドウ作成
root.title('注文システム')   #ウィンドウのタイトル
root.geometry('400x500')    #ウィンドウサイズ

#商品ボタン
frame = tk.Frame(root)  #ボタンをまとめるためのフレームを作成
frame.pack()    #ウィンドウにframeを配置

for product in products.keys():     #商品リストをループ
    #ボタンを押したらadd_to_cart(p)実行
    btn = tk.Button(frame, text=product, width=15, height=2, command=lambda p=product: add_to_cart(p))  
    btn.pack(pady=5)

#カート表示
cart_text = tk.Text(root, height=10, width=40)  #カートの内容を表示するテキストボックス
cart_text.pack()    #ウィンドウにcartを配置

#注文確定ボタン
#textボタンのラベル, command=押されたらconfirm_oder実行, bg='green', fg='white'ボタンの背景色を緑、文字色を白
confirm_btn = tk.Button(root, text='購入確定' , command=confirm_oder, bg='green', fg='white')   
confirm_btn.pack(pady=10)

#ウィンドウを開いたままにする(イベントループを開始)
root.mainloop()