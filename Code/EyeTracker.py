import cv2
import numpy as np
import os
import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import mediapipe as mp

# MediaPipeの初期化
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 視線追跡用のパラメータ
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def calculate_gaze_direction(eye_landmarks, frame_shape):
    """視線の方向を計算"""
    # 目の中心点を計算
    left_eye_center = np.mean(eye_landmarks[:6], axis=0)
    right_eye_center = np.mean(eye_landmarks[6:12], axis=0)
    
    # 両目の中心
    eyes_center = (left_eye_center + right_eye_center) / 2
    
    # 画面の中心からの相対位置を計算
    screen_center_x = frame_shape[1] / 2
    screen_center_y = frame_shape[0] / 2
    
    # 視線の方向ベクトル
    gaze_x = (eyes_center[0] - screen_center_x) / screen_center_x
    gaze_y = (eyes_center[1] - screen_center_y) / screen_center_y
    
    return gaze_x, gaze_y

def map_gaze_to_screen(gaze_x, gaze_y):
    """視線の方向を画面座標にマッピング"""
    # 視線の方向を画面座標に変換
    screen_x = int((gaze_x + 1) * SCREEN_WIDTH / 2)
    screen_y = int((gaze_y + 1) * SCREEN_HEIGHT / 2)
    
    # 画面範囲内に制限
    screen_x = max(0, min(SCREEN_WIDTH - 1, screen_x))
    screen_y = max(0, min(SCREEN_HEIGHT - 1, screen_y))
    
    return screen_x, screen_y

def draw_gaze_crosshair(frame, screen_x, screen_y, color=(0, 255, 0)):
    """視線位置に十字線を描画"""
    # 縦線
    cv2.line(frame, (screen_x, 0), (screen_x, frame.shape[0]), color, 2)
    # 横線
    cv2.line(frame, (0, screen_y), (frame.shape[1], screen_y), color, 2)
    
    # 中心に円を描画
    cv2.circle(frame, (screen_x, screen_y), 10, color, -1)
    cv2.circle(frame, (screen_x, screen_y), 15, color, 2)

def detect_eye_landmarks(face_mesh, frame):
    """顔メッシュから目のランドマークを検出"""
    # BGRからRGBに変換
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        
        # 左目のランドマーク（MediaPipe Face Meshのインデックス）
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        left_eye_landmarks = []
        for idx in left_eye_indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            left_eye_landmarks.append([x, y])
        
        # 右目のランドマーク
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        right_eye_landmarks = []
        for idx in right_eye_indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            right_eye_landmarks.append([x, y])
        
        return left_eye_landmarks, right_eye_landmarks
    
    return None, None

def classify_hand_gesture(hand_landmarks):
    """手のひらの形を分類（グー、チョキ、パー）"""
    # 手のランドマークの座標を取得
    landmarks = []
    for lm in hand_landmarks.landmark:
        landmarks.append([lm.x, lm.y, lm.z])
    
    # 手のひらの大きさを計算（距離の指標として使用）
    # 手首（0番）から中指の付け根（9番）までの距離
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    palm_size = np.linalg.norm(np.array(wrist) - np.array(middle_mcp))
    
    # 距離に応じて動的に閾値を調整
    # 手のひらが大きい（近距離）→ 閾値を大きくする
    # 手のひらが小さい（遠距離）→ 閾値を小さくする
    base_threshold = 0.08
    distance_factor = 1.0
    
    if palm_size > 0.15:  # 近距離（手が大きい）
        distance_factor = 1.5  # 閾値を1.5倍に
    elif palm_size < 0.08:  # 遠距離（手が小さい）
        distance_factor = 0.7  # 閾値を0.7倍に
    
    threshold = base_threshold * distance_factor
    
    # 親指の先端（4番）と親指の付け根（2番）の距離
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[2]
    
    # 人差し指の先端（8番）と人差し指の付け根（5番）の距離
    index_tip = landmarks[8]
    index_mcp = landmarks[5]
    
    # 中指の先端（12番）と中指の付け根（9番）の距離
    middle_tip = landmarks[12]
    middle_mcp = landmarks[9]
    
    # 薬指の先端（16番）と薬指の付け根（13番）の距離
    ring_tip = landmarks[16]
    ring_mcp = landmarks[13]
    
    # 小指の先端（20番）と小指の付け根（17番）の距離
    pinky_tip = landmarks[20]
    pinky_mcp = landmarks[17]
    
    # 各指が伸びているかどうかを判定
    # 指の先端と付け根の距離が一定以上なら伸びているとみなす
    thumb_extended = np.linalg.norm(np.array(thumb_tip) - np.array(thumb_ip)) > threshold
    index_extended = np.linalg.norm(np.array(index_tip) - np.array(index_mcp)) > threshold
    middle_extended = np.linalg.norm(np.array(middle_tip) - np.array(middle_mcp)) > threshold
    ring_extended = np.linalg.norm(np.array(ring_tip) - np.array(ring_mcp)) > threshold
    pinky_extended = np.linalg.norm(np.array(pinky_tip) - np.array(pinky_mcp)) > threshold
    
    # 伸びている指の数をカウント
    extended_fingers = sum([thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended])
    
    # シンプルな判定：伸びている指の数だけで判定
    if extended_fingers == 0:
        return "グー"
    elif extended_fingers == 2:
        return "チョキ"
    elif extended_fingers == 5:
        return "パー"
    else:
        # 1本、3本、4本の場合は、最も近い形に判定
        if extended_fingers <= 1:
            return "グー"
        elif extended_fingers >= 4:
            return "パー"
        else:
            return "チョキ"

def save_screenshot(frame):
    """スクリーンショットを保存"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"docs/Webcam/screenshot_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Screenshot saved: {filename}")

def main():
    # カメラの初期化
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # 録画用の設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    recording = False
    video_writer = None
    recording_start_time = None
    
    # スクリーンショット用のディレクトリ作成
    os.makedirs("docs/Webcam", exist_ok=True)
    
    # MediaPipe Face Meshの初期化
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # カメラを水平反転
            frame = cv2.flip(frame, 1)
            
            # 目のランドマークを検出
            left_eye_landmarks, right_eye_landmarks = detect_eye_landmarks(face_mesh, frame)
            
            if left_eye_landmarks and right_eye_landmarks:
                # 両目のランドマークを結合
                all_eye_landmarks = np.array(left_eye_landmarks + right_eye_landmarks)
                
                # 視線の方向を計算
                gaze_x, gaze_y = calculate_gaze_direction(all_eye_landmarks, frame.shape)
                
                # 視線位置を画面座標にマッピング
                screen_x, screen_y = map_gaze_to_screen(gaze_x, gaze_y)
                
                # 視線位置に十字線を描画
                draw_gaze_crosshair(frame, screen_x, screen_y)
                
                # 視線座標を表示
                gaze_text = f"Gaze: ({screen_x}, {screen_y})"
                cv2.putText(frame, gaze_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 目のランドマークを描画
                for landmark in left_eye_landmarks + right_eye_landmarks:
                    cv2.circle(frame, tuple(landmark), 2, (0, 255, 0), -1)
            
            # 手の検出
            with mp.solutions.hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            ) as hands:
                # BGRからRGBに変換
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        # 手の骨格を描画
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp.solutions.hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # 手の形を分類
                        gesture = classify_hand_gesture(hand_landmarks)
                        
                        # 手の上にテキストを表示
                        if gesture == "グー":
                            # グーの時は中指の第一関節の上に表示
                            middle_finger_ip = hand_landmarks.landmark[11]  # 中指の第一関節
                            x = int(middle_finger_ip.x * frame.shape[1])
                            y = int(middle_finger_ip.y * frame.shape[0])
                            text_y = y - 60  # 第一関節の上に配置
                        else:
                            # チョキやパーの時は中指の上に表示
                            middle_finger_tip = hand_landmarks.landmark[12]  # 中指の先端
                            x = int(middle_finger_tip.x * frame.shape[1])
                            y = int(middle_finger_tip.y * frame.shape[0])
                            text_y = y - 80  # 中指の上に配置
                        
                        # PILを使用して日本語テキストを描画
                        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        draw = ImageDraw.Draw(frame_pil)
                        try:
                            font = ImageFont.truetype("msgothic.ttc", 40)  # MS Gothic
                        except:
                            try:
                                font = ImageFont.truetype("arial.ttf", 40)  # Arial
                            except:
                                font = ImageFont.load_default()
                        draw.text((x-30, text_y), gesture, fill=(0, 255, 0), font=font)
                        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
            
            # 制御テキストを画面下部に表示
            control_text = "ESC: Exit | SPACE: Screenshot | R: Record Start/Stop"
            text_size = cv2.getTextSize(control_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = frame.shape[0] - 20
            cv2.putText(frame, control_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 録画状態を表示
            if recording:
                recording_time = time.time() - recording_start_time
                recording_text = f"Recording: {recording_time:.1f}s"
                cv2.putText(frame, recording_text, (10, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 画面に表示
            cv2.imshow('Eye Tracker & Hand Gesture', frame)
            
            # キー入力の処理
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESCキー
                break
            elif key == ord(' '):  # スペースキー
                save_screenshot(frame)
            elif key == ord('r') or key == ord('R'):  # Rキー
                if not recording:
                    # 録画開始
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"docs/Webcam/recording_{timestamp}.mp4"
                    video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (1280, 720))
                    recording = True
                    recording_start_time = time.time()
                    print(f"Recording started: {filename}")
                else:
                    # 録画停止
                    if video_writer:
                        video_writer.release()
                    recording = False
                    print("Recording stopped")
            
            # 録画中の場合、フレームを保存
            if recording and video_writer:
                video_writer.write(frame)
    
    # クリーンアップ
    cap.release()
    if video_writer:
        video_writer.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


