<?php
session_start();

//セッション内に認証コードが保存されていない場合
if (!isset($_SESSION['code'])){
    echo "セッションが期限切れです。最初からやり直してください。";
    exit;
}

//入力された認証コードを取得
$user_code = $_POST['Ninsyou'];

if (empty($user_code)){
    echo "認証コードを入力してください。";
    exit;
}

//Ninsyou.phpのセッションで保存されてる認証コードを取得
$correct_code = $_SESSION['code'];

//認証コードを照合
if($user_code == $correct_code) {
    echo "登録完了しました";

    //セッションクリア
    session_unset();
    session_destroy();
} else {
    echo "認証コードが間違っています。もう一度試してください";
}