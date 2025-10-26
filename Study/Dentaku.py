# Dentaku.py - シンプルな電卓プログラム
# ユーザーから数値と演算子を入力し、その結果を表示する。
# このプログラムでは足し算、引き算、掛け算、割り算を行う。

#最初の数値を入力してもらう
num1 = float(input('最初の数値を入力してください： '))

#演算子を入力してもらう（+,*,-,/）
operator = input('演算子を入力してください(+, -, *, /):')

#次の数字を入力してもらう
num2 = float(input('次の数字を入力してください： '))

#演算子に元図いて計算をする
if operator == '+' : 
    result = num1 + num2
    
elif operator == '-':
    result = num1 - num2
    
elif operator == '*':
    result = num1 * num2

elif operator == '/':
    if num2 != 0: #0で割る場合のエラーチェック
        result = num1 / num2
    else:
        result = 'エラー： 0で割ることはできません'
else:
    result = '不正な演算子です'

    #計算結果を表示
print('結果： ', result)