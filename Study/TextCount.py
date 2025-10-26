import re
from collections import Counter

#テキストの受け取り
text = input('テキストを入力してください： ').strip()

#入力がからだった場合の処理
if not text:
    print('入力がありません')
else:
    #入力されたテキストを表示
    print('入力されたテキスト： ', text)

    #文字数をカウント（空白や改行も含む）
    count1 = len(text)
    #カウントされた文字数を表示
    print('文字数： ', count1)

    #正規表現で単語を抽出（日本語も含む）
    words = re.findall(r'\b\w+\b|[ぁ-んァ-ンー一-龠]+', text.lower())

    if words:
        print('分解された単語： ', words)
        #単語数をカウント
        count2 = len(words)
        print('単語数： ', count2)

        #単語の出現回数をカウント
        word_count = Counter(words)
        print('単語の出現回数： ', word_count)

        #最も出た単語を表示
        most_common_word = word_count.most_common(1)
        print('最も出た単語： ', most_common_word)

        #結果をファイルに保存
        with open('text_analysis_result.txt', 'w', encoding='utf-8') as file:
            F = file.write
            F(f'入力されたテキスト： {text}\n')
            F(f'文字数： {count1}\n')
            F(f'単語数： {count2}\n')
            F(f'単語の出現回数： {word_count}\n')
            F(f'最も出た単語： {most_common_word}\n')

            print('結果が "text_analysis_result.txt" に保存されました')
    else:
        print('単語が見つかりません')
