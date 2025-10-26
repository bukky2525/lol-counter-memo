#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube音声キャプチャーユーティリティ
"""

import subprocess
import threading
import time
import os
from pathlib import Path
from typing import Optional, Callable
import json

class YouTubeAudioCapture:
    """YouTubeの音声をキャプチャするクラス"""
    
    def __init__(self):
        """初期化"""
        self.is_capturing = False
        self.capture_thread = None
        self.audio_callback = None
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # yt-dlpのインストール確認
        self.yt_dlp_available = self._check_yt_dlp()
        
    def _check_yt_dlp(self) -> bool:
        """yt-dlpが利用可能かチェック"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def install_yt_dlp(self):
        """yt-dlpをインストール"""
        try:
            print("📦 yt-dlpをインストールしています...")
            subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            self.yt_dlp_available = True
            print("✅ yt-dlpのインストールが完了しました")
        except Exception as e:
            print(f"❌ yt-dlpのインストールに失敗しました: {e}")
            print("手動でインストールしてください: pip install yt-dlp")
    
    def start_capture(self, url: str, callback: Optional[Callable] = None):
        """YouTube音声キャプチャーを開始"""
        if not self.yt_dlp_available:
            print("❌ yt-dlpがインストールされていません")
            self.install_yt_dlp()
            if not self.yt_dlp_available:
                return False
        
        if self.is_capturing:
            print("⚠️ 既にキャプチャーが実行中です")
            return False
        
        try:
            self.audio_callback = callback
            self.is_capturing = True
            
            # キャプチャースレッドを開始
            self.capture_thread = threading.Thread(
                target=self._capture_audio, 
                args=(url,)
            )
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            print(f"🎬 YouTube音声キャプチャーを開始しました: {url}")
            return True
            
        except Exception as e:
            print(f"❌ キャプチャー開始エラー: {e}")
            self.is_capturing = False
            return False
    
    def stop_capture(self):
        """YouTube音声キャプチャーを停止"""
        self.is_capturing = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        print("🛑 YouTube音声キャプチャーを停止しました")
    
    def _capture_audio(self, url: str):
        """音声キャプチャー処理"""
        try:
            # 一時ファイル名を生成
            timestamp = int(time.time())
            output_file = self.temp_dir / f"audio_{timestamp}.wav"
            
            # yt-dlpで音声をダウンロード
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'wav',
                '--audio-quality', '0',
                '--output', str(output_file),
                '--no-playlist',
                url
            ]
            
            print("📥 音声をダウンロードしています...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 音声ダウンロード完了: {output_file}")
                
                # コールバックが設定されている場合は実行
                if self.audio_callback:
                    self.audio_callback(str(output_file))
                
                # キャプチャー中はファイルを保持
                while self.is_capturing:
                    time.sleep(1)
                
                # 一時ファイルを削除
                if output_file.exists():
                    output_file.unlink()
                    print(f"🗑️ 一時ファイルを削除しました: {output_file}")
            else:
                print(f"❌ 音声ダウンロードに失敗しました: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 音声キャプチャーエラー: {e}")
        finally:
            self.is_capturing = False
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """動画情報を取得"""
        if not self.yt_dlp_available:
            return None
        
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0)
                }
            
        except Exception as e:
            print(f"動画情報取得エラー: {e}")
        
        return None
    
    def search_videos(self, query: str, max_results: int = 5) -> list:
        """動画を検索"""
        if not self.yt_dlp_available:
            return []
        
        try:
            # YouTube検索URL
            search_url = f"ytsearch{max_results}:{query}"
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                search_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                videos = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            info = json.loads(line)
                            videos.append({
                                'title': info.get('title', 'Unknown'),
                                'url': info.get('webpage_url', ''),
                                'duration': info.get('duration', 0),
                                'uploader': info.get('uploader', 'Unknown'),
                                'view_count': info.get('view_count', 0)
                            })
                        except:
                            continue
                
                return videos
            
        except Exception as e:
            print(f"動画検索エラー: {e}")
        
        return []
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        self.stop_capture()
        
        # 一時ファイルを削除
        try:
            for file in self.temp_dir.glob("audio_*.wav"):
                file.unlink()
            self.temp_dir.rmdir()
        except:
            pass

if __name__ == "__main__":
    # テスト用
    print("🎬 YouTube音声キャプチャーテスト")
    print("=" * 40)
    
    capture = YouTubeAudioCapture()
    
    # yt-dlpの確認
    if not capture.yt_dlp_available:
        print("yt-dlpがインストールされていません")
        capture.install_yt_dlp()
    
    # 動画検索テスト
    print("\n🔍 動画検索テスト:")
    videos = capture.search_videos("music", 3)
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']}")
        print(f"   アップローダー: {video['uploader']}")
        print(f"   再生時間: {video['duration']}秒")
        print(f"   視聴回数: {video['view_count']:,}")
        print()
    
    # 動画情報取得テスト
    if videos:
        print("📊 動画情報取得テスト:")
        info = capture.get_video_info(videos[0]['url'])
        if info:
            print(f"タイトル: {info['title']}")
            print(f"アップローダー: {info['uploader']}")
            print(f"再生時間: {info['duration']}秒")
            print(f"視聴回数: {info['view_count']:,}")
            print(f"いいね数: {info['like_count']:,}")
    
    print("\n✅ テスト完了")
    capture.cleanup()
