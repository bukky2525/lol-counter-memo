def quick_sort(data, first, last):
    if first >= last:
        return  # ソート終了

    pivot = data[(first + last) // 2]  # ピボットの選択
    i = first
    j = last

    while True:
        while data[i] < pivot:  # ピボットより小さい値を探す
            i += 1
        while data[j] > pivot:  # ピボットより大きい値を探す
            j -= 1
        if i >= j:  # ポインタが交差したら終了
            break
        data[i], data[j] = data[j], data[i]  # 値を入れ替える
        i += 1
        j -= 1

    print(" ".join(map(str, data)))  # α: ソートの途中経過を出力

    # 左側を再帰的にソート
    if first < i - 1:
        quick_sort(data, first, i - 1)
    # 右側を再帰的にソート
    if j + 1 < last:
        quick_sort(data, j + 1, last)

# 初期データ
data = [2, 1, 3, 5, 4]

# クイックソート実行
quick_sort(data, 0, len(data) - 1)

# 最終結果の出力
print("Sorted:", " ".join(map(str, data)))
