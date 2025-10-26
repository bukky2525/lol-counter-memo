#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube音声リアルタイムビジュアライザー
"""

import numpy as np
import pyaudio
import librosa
import sounddevice as sd
from scipy import signal
from scipy.fft import fft
import threading
import time
import queue
from typing import List, Tuple, Optional, Dict
import cv2
from PIL import Image, ImageDraw, ImageFont
import os

class AudioVisualizer:
    """リアルタイムオーディオビジュアライザー"""
    
    def __init__(self, sample_rate=44100, chunk_size=1024, num_bars=32):
        """初期化"""
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.num_bars = num_bars
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_thread = None
        
        # オーディオ設定
        self.channels = 1
        self.format = pyaudio.paFloat32
        
        # ビジュアライゼーション設定
        self.bar_heights = np.zeros(num_bars)
        self.frequency_bands = self._create_frequency_bands()
        
        # 色設定
        self.colors = self._create_color_palette()
        
        # オーディオストリーム
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def _create_frequency_bands(self) -> List[Tuple[int, int]]:
        """周波数帯域を作成"""
        bands = []
        # 低周波数から高周波数まで対数的に分割
        low_freq = 20
        high_freq = 20000
        
        for i in range(self.num_bars):
            start_freq = int(low_freq * (high_freq / low_freq) ** (i / self.num_bars))
            end_freq = int(low_freq * (high_freq / low_freq) ** ((i + 1) / self.num_bars))
            bands.append((start_freq, end_freq))
        
        return bands
    
    def _create_color_palette(self) -> List[Tuple[int, int, int]]:
        """カラーパレットを作成"""
        colors = []
        # 低周波数（青）から高周波数（赤）へのグラデーション
        for i in range(self.num_bars):
            ratio = i / (self.num_bars - 1)
            r = int(255 * ratio)
            g = int(100 + 155 * (1 - ratio))
            b = int(255 * (1 - ratio))
            colors.append((r, g, b))
        return colors
    
    def start_recording(self):
        """音声録音を開始"""
        if self.is_recording:
            return
        
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.audio_thread = threading.Thread(target=self._audio_processing_thread)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            
            print("🎤 音声録音を開始しました")
            
        except Exception as e:
            print(f"❌ 音声録音開始エラー: {e}")
    
    def stop_recording(self):
        """音声録音を停止"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        
        print("🛑 音声録音を停止しました")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """オーディオコールバック"""
        if self.is_recording:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def _audio_processing_thread(self):
        """音声処理スレッド"""
        while self.is_recording:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get_nowait()
                    self._process_audio_chunk(audio_data)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"音声処理エラー: {e}")
                time.sleep(0.1)
    
    def _process_audio_chunk(self, audio_data):
        """音声チャンクを処理"""
        try:
            # バイトデータをnumpy配列に変換
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # FFTで周波数解析
            fft_data = fft(audio_array)
            magnitude = np.abs(fft_data[:len(fft_data)//2])
            
            # 各周波数帯域のエネルギーを計算
            for i, (start_freq, end_freq) in enumerate(self.frequency_bands):
                start_bin = int(start_freq * self.chunk_size / self.sample_rate)
                end_bin = int(end_freq * self.chunk_size / self.sample_rate)
                
                if start_bin < len(magnitude) and end_bin < len(magnitude):
                    band_energy = np.mean(magnitude[start_bin:end_bin])
                    
                    # バーの高さを更新（スムージング付き）
                    target_height = min(1.0, band_energy / 1000)  # 正規化
                    self.bar_heights[i] = 0.8 * self.bar_heights[i] + 0.2 * target_height
                    
        except Exception as e:
            print(f"音声チャンク処理エラー: {e}")
    
    def get_visualization_data(self) -> Tuple[np.ndarray, List[Tuple[int, int, int]]]:
        """ビジュアライゼーションデータを取得"""
        return self.bar_heights.copy(), self.colors.copy()
    
    def create_visualization_image(self, width=240, height=240) -> Image.Image:
        """ビジュアライゼーション画像を作成"""
        try:
            # 画像を作成
            image = Image.new('RGB', (width, height), (0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # バーの幅と間隔を計算
            bar_width = width // (self.num_bars + 1)
            bar_spacing = (width - bar_width * self.num_bars) // (self.num_bars + 1)
            
            # 各バーを描画
            for i in range(self.num_bars):
                x = bar_spacing + i * (bar_width + bar_spacing)
                bar_height = int(self.bar_heights[i] * height * 0.8)
                y = height - bar_height
                
                # バーの色を取得
                color = self.colors[i]
                
                # バーを描画
                draw.rectangle([x, y, x + bar_width, height], fill=color)
                
                # グラデーション効果（上部を明るく）
                for j in range(bar_height):
                    alpha = int(255 * (j / bar_height))
                    bright_color = tuple(min(255, c + alpha // 3) for c in color)
                    draw.line([x, y + j, x + bar_width, y + j], fill=bright_color)
            
            # 中央に音声レベルインジケーターを追加
            overall_level = np.mean(self.bar_heights)
            if overall_level > 0.1:  # 音声が検出された場合
                # 円形のインジケーター
                center_x, center_y = width // 2, height // 2
                radius = int(20 + overall_level * 30)
                draw.ellipse([center_x - radius, center_y - radius, 
                            center_x + radius, center_y + radius], 
                           fill=(255, 255, 255), outline=(100, 100, 100))
            
            return image
            
        except Exception as e:
            print(f"ビジュアライゼーション画像作成エラー: {e}")
            # エラー時は空の画像を返す
            return Image.new('RGB', (width, height), (0, 0, 0))
    
    def get_audio_levels(self) -> Dict[str, float]:
        """音声レベルの詳細情報を取得"""
        try:
            # 低周波数、中周波数、高周波数のレベル
            low_freq = np.mean(self.bar_heights[:self.num_bars//3])
            mid_freq = np.mean(self.bar_heights[self.num_bars//3:2*self.num_bars//3])
            high_freq = np.mean(self.bar_heights[2*self.num_bars//3:])
            
            # 全体のレベル
            overall_level = np.mean(self.bar_heights)
            
            # ピーク検出
            peak_level = np.max(self.bar_heights)
            
            return {
                'overall': overall_level,
                'low_freq': low_freq,
                'mid_freq': mid_freq,
                'high_freq': high_freq,
                'peak': peak_level,
                'bars': self.bar_heights.tolist()
            }
            
        except Exception as e:
            print(f"音声レベル取得エラー: {e}")
            return {}
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()

if __name__ == "__main__":
    # テスト用
    print("🎵 オーディオビジュアライザーテスト")
    print("=" * 40)
    
    visualizer = AudioVisualizer()
    
    try:
        print("音声録音を開始します...")
        print("何か音を出してください（Ctrl+Cで停止）")
        
        visualizer.start_recording()
        
        # リアルタイム表示
        while True:
            levels = visualizer.get_audio_levels()
            if levels:
                # コンソールにバーを表示
                bars = "".join(["█" if h > 0.1 else "░" for h in levels['bars'][:20]])
                print(f"\r音声レベル: {bars} | 全体: {levels['overall']:.3f}", end='')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 テストを停止しました")
    finally:
        visualizer.cleanup()
