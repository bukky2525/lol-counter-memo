import cv2      # 撮影するライブラリ
import datetime # 現在時刻を取得するライブラリ
import time     # 時間を計測するライブラリ

# 使用するカメラのデバイス番号を指定（通常は0）
cap = cv2.VideoCapture(1)

# 動画保存設定
dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # ファイル名
codec = cv2.VideoWriter_fourcc(*"mp4v")                 # コーデック
out = None                                              # 保存する動画
start_time = 0                                          # 録画開始時間
recording = False                                       # 録画フラグ

# 撮影開始
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 操作説明
    cv2.putText(frame, f"[s]:Start REC", (5, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(frame, f"[e]:End REC", (5, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(frame, f"[q]:Quit", (5, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # 録画が開始されたらフレームを動画として保存
    if recording:
        out.write(frame)
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        cv2.putText(frame, f"REC:{elapsed_str}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # フレームを表示
    cv2.imshow('Frame', frame)

    # キー取得
    key = cv2.waitKey(1) & 0xFF

    # 録画開始：キーが[s] かつ 録画していない
    if key == ord('s') and not recording:
        out = cv2.VideoWriter(f"{dt}.mp4", codec, 20.0, (640, 480))
        recording = True
        start_time = time.time()
        print("録画を開始しました。")

    # 録画終了：キーが[e] かつ 録画中
    elif key == ord('e') and recording:
        recording = False
        out.release()
        print("録画を終了しました。")

    # アプリ終了：キーが[q]
    elif key == ord('q'):
        print("アプリを終了しました。")
        break

# 後片付け
cap.release()
if out:
    out.release()
cv2.destroyAllWindows()