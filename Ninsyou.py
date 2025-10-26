import secrets
import string

def generate_verification_code(length=6):
    #使用する文字セット（数字とアルファベット）
    characters = string.ascii_letters + string.digits
    #ランダムにえたんだ文字列生成
    code = ''.join(secrets.choice(characters) for i in range(length))
    return code


#認証コード生成
verfication_code = generate_verification_code()
print(verfication_code)
