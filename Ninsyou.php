<?php
// セッション開始
session_start();

/* 
// $_POST["email"] と $_POST["pass"] が設定されている場合のみ処理を実行
if (isset($_POST["email"]) && isset($_POST["pass"])) {
    $email = $_POST["email"];
    $pass = $_POST["pass"];
} else {
    echo "メールアドレスまたはパスワードが送信されていません。";
    exit; // エラー時はスクリプトを終了
}
*/

// Ninsyou.pyを呼び出す
$command = escapeshellcmd("python3 Ninsyou.py");  // Ninsyou.pyを実行
$code = shell_exec($command); // 実行結果を取得

// 改行とスペースを取り除く
$code = trim($code);

// 認証コードをセッションに保存
$_SESSION['code'] = $code;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>認証コード</title>
</head>
<body>
    <h1>認証コード送信完了</h1>
    <!--<p>メールアドレス：<?php echo $email; ?></p>-->
    <p>ようこそ、認証コードを生成しました</p>

    <!-- 認証コードを表示 -->
    <p>認証コード：<?php echo $code; ?></p>

    <form id="form1" action="form.py" method="post">

        <button type="submit">認証コードを送信</button>
    </form>

    <form id="form2" action="verify.php" method="post">
        <label for="Ninsyou">認証コード：</label>
        <input type="text" id="Ninsyou" name="Ninsyou" required>
        
        <button type="submit">認証</button>
    </form>
</body>
</html>