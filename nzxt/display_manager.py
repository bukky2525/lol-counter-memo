#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NZXT Kraken ディスプレイ表示マネージャー
"""

import time
import threading
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from audio_visualizer import AudioVisualizer

class DisplayManager:
    """NZXT Krakenのディスプレイ表示を管理するクラス"""
    
    def __init__(self, controller):
        """初期化"""
        self.controller = controller
        self.display_width = 240
        self.display_height = 240
        self.current_mode = 'idle'
        self.is_active = False
        
        # オーディオビジュアライザー
        self.audio_visualizer = AudioVisualizer()
        
        # 表示スレッド
        self.display_thread = None
        
        # フォント設定
        try:
            # Windows標準フォントを使用
            self.font_small = ImageFont.truetype("arial.ttf", 12)
            self.font_medium = ImageFont.truetype("arial.ttf", 16)
            self.font_large = ImageFont.truetype("arial.ttf", 20)
        except:
            # フォントが見つからない場合はデフォルト
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def start_audio_visualization(self):
        """オーディオビジュアライゼーションを開始"""
        if self.current_mode == 'audio':
            return
        
        try:
            self.current_mode = 'audio'
            self.is_active = True
            
            # オーディオ録音を開始
            self.audio_visualizer.start_recording()
            
            # 表示スレッドを開始
            self.display_thread = threading.Thread(target=self._audio_display_loop)
            self.display_thread.daemon = True
            self.display_thread.start()
            
            print("🎵 オーディオビジュアライゼーションを開始しました")
            
        except Exception as e:
            print(f"❌ オーディオビジュアライゼーション開始エラー: {e}")
    
    def stop_audio_visualization(self):
        """オーディオビジュアライゼーションを停止"""
        self.is_active = False
        self.current_mode = 'idle'
        
        if self.audio_visualizer:
            self.audio_visualizer.stop_recording()
        
        if self.display_thread:
            self.display_thread.join(timeout=1)
        
        print("🛑 オーディオビジュアライゼーションを停止しました")
    
    def _audio_display_loop(self):
        """オーディオ表示ループ"""
        while self.is_active and self.current_mode == 'audio':
            try:
                # ビジュアライゼーション画像を作成
                image = self.audio_visualizer.create_visualization_image(
                    self.display_width, self.display_height
                )
                
                # NZXTディスプレイに表示
                self._send_to_display(image)
                
                # 音声レベル情報を取得してコンソールに表示
                levels = self.audio_visualizer.get_audio_levels()
                if levels:
                    self._print_audio_info(levels)
                
                time.sleep(0.05)  # 20FPS
                
            except Exception as e:
                print(f"表示ループエラー: {e}")
                time.sleep(0.1)
    
    def _send_to_display(self, image: Image.Image):
        """画像をNZXTディスプレイに送信"""
        try:
            # ここでNZXT CAM APIを使用してディスプレイに画像を送信
            # 実際の実装では、NZXT CAMのSDKやAPIを使用
            
            # 仮の実装：画像をファイルに保存（デバッグ用）
            debug_path = "debug_display.png"
            image.save(debug_path)
            
            # TODO: NZXT CAM APIを使用した実際のディスプレイ制御
            # self.controller.send_image_to_display(image)
            
        except Exception as e:
            print(f"ディスプレイ送信エラー: {e}")
    
    def _print_audio_info(self, levels: Dict[str, float]):
        """音声情報をコンソールに表示"""
        try:
            # バーのビジュアル表示
            bars = "".join(["█" if h > 0.1 else "░" for h in levels['bars'][:20]])
            
            # 周波数帯域別のレベル
            low_level = "█" * int(levels['low_freq'] * 10)
            mid_level = "█" * int(levels['mid_freq'] * 10)
            high_level = "█" * int(levels['high_freq'] * 10)
            
            print(f"\r🎵 音声レベル: {bars}")
            print(f"   🔵 低周波数: {low_level:<10} ({levels['low_freq']:.3f})")
            print(f"   🟢 中周波数: {mid_level:<10} ({levels['mid_freq']:.3f})")
            print(f"   🔴 高周波数: {high_level:<10} ({levels['high_freq']:.3f})")
            print(f"   📊 全体レベル: {levels['overall']:.3f} | ピーク: {levels['peak']:.3f}")
            
        except Exception as e:
            print(f"音声情報表示エラー: {e}")
    
    def show_system_info(self, cpu_temp: float, cpu_usage: float, 
                         gpu_temp: float, memory_usage: float):
        """システム情報を表示"""
        try:
            # システム情報画像を作成
            image = self._create_system_info_image(cpu_temp, cpu_usage, gpu_temp, memory_usage)
            
            # ディスプレイに送信
            self._send_to_display(image)
            
        except Exception as e:
            print(f"システム情報表示エラー: {e}")
    
    def _create_system_info_image(self, cpu_temp: float, cpu_usage: float,
                                 gpu_temp: float, memory_usage: float) -> Image.Image:
        """システム情報画像を作成"""
        try:
            # 画像を作成
            image = Image.new('RGB', (self.display_width, self.display_height), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # タイトル
            title = "SYSTEM INFO"
            title_bbox = draw.textbbox((0, 0), title, font=self.font_large)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.display_width - title_width) // 2
            draw.text((title_x, 10), title, fill=(255, 255, 255), font=self.font_large)
            
            # CPU情報
            cpu_text = f"CPU: {cpu_temp:.1f}°C"
            draw.text((20, 50), cpu_text, fill=(255, 100, 100), font=self.font_medium)
            
            # CPU使用率バー
            cpu_bar_width = int((self.display_width - 40) * cpu_usage / 100)
            draw.rectangle([20, 80, 20 + cpu_bar_width, 95], fill=(255, 100, 100))
            draw.rectangle([20, 80, self.display_width - 20, 95], outline=(100, 100, 100))
            
            # GPU情報
            gpu_text = f"GPU: {gpu_temp:.1f}°C"
            draw.text((20, 110), gpu_text, fill=(100, 255, 100), font=self.font_medium)
            
            # メモリ情報
            mem_text = f"RAM: {memory_usage:.1f}%"
            draw.text((20, 140), mem_text, fill=(100, 100, 255), font=self.font_medium)
            
            # メモリ使用率バー
            mem_bar_width = int((self.display_width - 40) * memory_usage / 100)
            draw.rectangle([20, 170, 20 + mem_bar_width, 185], fill=(100, 100, 255))
            draw.rectangle([20, 170, self.display_width - 20, 185], outline=(100, 100, 100))
            
            # 時刻
            time_text = time.strftime("%H:%M:%S")
            time_bbox = draw.textbbox((0, 0), time_text, font=self.font_small)
            time_width = time_bbox[2] - time_bbox[0]
            time_x = (self.display_width - time_width) // 2
            draw.text((time_x, self.display_height - 30), time_text, fill=(150, 150, 150), font=self.font_small)
            
            return image
            
        except Exception as e:
            print(f"システム情報画像作成エラー: {e}")
            return Image.new('RGB', (self.display_width, self.display_height), (0, 0, 0))
    
    def show_custom_text(self, text: str):
        """カスタムテキストを表示"""
        try:
            # カスタムテキスト画像を作成
            image = self._create_custom_text_image(text)
            
            # ディスプレイに送信
            self._send_to_display(image)
            
        except Exception as e:
            print(f"カスタムテキスト表示エラー: {e}")
    
    def _create_custom_text_image(self, text: str) -> Image.Image:
        """カスタムテキスト画像を作成"""
        try:
            # 画像を作成
            image = Image.new('RGB', (self.display_width, self.display_height), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # テキストを中央に配置
            text_bbox = draw.textbbox((0, 0), text, font=self.font_large)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (self.display_width - text_width) // 2
            text_y = (self.display_height - text_height) // 2
            
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=self.font_large)
            
            return image
            
        except Exception as e:
            print(f"カスタムテキスト画像作成エラー: {e}")
            return Image.new('RGB', (self.display_width, self.display_height), (0, 0, 0))
    
    def show_image(self, image_path: str):
        """画像ファイルを表示"""
        try:
            # 画像を読み込み
            image = Image.open(image_path)
            
            # ディスプレイサイズにリサイズ
            image = image.resize((self.display_width, self.display_height), Image.Resampling.LANCZOS)
            
            # ディスプレイに送信
            self._send_to_display(image)
            
        except Exception as e:
            print(f"画像表示エラー: {e}")
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        self.stop_audio_visualization()
        
        if self.audio_visualizer:
            self.audio_visualizer.cleanup()

if __name__ == "__main__":
    # テスト用
    print("🖥️ ディスプレイマネージャーテスト")
    print("=" * 40)
    
    # 仮のコントローラーを作成
    class MockController:
        def __init__(self):
            pass
    
    controller = MockController()
    display = DisplayManager(controller)
    
    print("1. システム情報表示テスト")
    display.show_system_info(65.5, 45.2, 72.1, 68.9)
    time.sleep(2)
    
    print("2. カスタムテキスト表示テスト")
    display.show_custom_text("Hello NZXT!")
    time.sleep(2)
    
    print("3. オーディオビジュアライゼーションテスト")
    display.start_audio_visualization()
    time.sleep(5)
    display.stop_audio_visualization()
    
    print("✅ テスト完了")
    display.cleanup()
