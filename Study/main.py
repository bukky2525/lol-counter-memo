# 必要なライブラリをインポート
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# サンプルデータ（X: 入力データ, y: 出力データ）
x = np.array([[12], [24], [35], [41], [5]])
y = np.array([1, 2, 3, 4, 5])

#線形回帰モデルのインスタンスを作成
model = LinearRegression()

#モデルを訓練
model.fit(x, y)

#予測を行う
y_pred = model.predict(x)

#結果をプロット
plt.scatter(x, y, color='blue', label='データポイント')
plt.plot(x, y_pred, color='red', label='予測直線')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()
