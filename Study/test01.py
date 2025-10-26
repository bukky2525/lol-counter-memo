# 入力を受け取り、空白で区切ってリストに変換
numbers = input().split()

# 文字列を整数に変換
numbers = list(map(int, numbers))

# 最大値と最小値を表示
print("最大値:", max(numbers))
print("最小値:", min(numbers))
