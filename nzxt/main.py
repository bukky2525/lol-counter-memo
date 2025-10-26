#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NZXT Kraken オーディオビジュアライザーメインスクリプト
"""

import sys
import time
import argparse
from pathlib import Path

# プロジェクトのモジュールをインポート
from nzxt_controller import NZXTController
from system_monitor import SystemMonitor
from display_manager import DisplayManager

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='NZXT Kraken オーディオビジュアライザー')
    parser.add_argument('--mode', choices=['audio', 'monitor', 'custom', 'image'], 
                       default='audio', help='表示モード')
    parser.add_argument('--text', type=str, help='カスタムテキスト')
    parser.add_argument('--image', type=str, help='画像ファイルパス')
    parser.add_argument('--interval', type=int, default=1, help='更新間隔（秒）')
    parser.add_argument('--test', action='store_true', help='テストモード')
    
    args = parser.parse_args()
    
    try:
        # NZXTコントローラーを初期化
        controller = NZXTController()
        
        if not args.test:
            if not controller.is_available():
                print("❌ NZXT Krakenが検出されませんでした")
                print("NZXT CAMソフトウェアが起動しているか確認してください")
                print("テストモードで実行する場合は --test オプションを使用してください")
                return 1
            
            print("✅ NZXT Krakenが検出されました")
        else:
            print("🧪 テストモードで実行します")
        
        # 表示マネージャーを初期化
        display = DisplayManager(controller)
        
        if args.mode == 'audio':
            # オーディオビジュアライゼーションモード（メイン機能）
            print("🎵 オーディオビジュアライゼーションモードを開始します...")
            print("YouTubeやその他の音声を再生して、リアルタイムでビジュアライゼーションを確認してください")
            print("Ctrl+Cで停止")
            
            try:
                # オーディオビジュアライゼーションを開始
                display.start_audio_visualization()
                
                # メインループ
                while True:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\n\n🛑 オーディオビジュアライゼーションを停止しました")
                display.stop_audio_visualization()
                
        elif args.mode == 'monitor':
            # システムモニターモード
            monitor = SystemMonitor()
            print("🖥️ システムモニターモードを開始します...")
            
            try:
                while True:
                    # システム情報を取得
                    cpu_temp = monitor.get_cpu_temperature()
                    cpu_usage = monitor.get_cpu_usage()
                    gpu_temp = monitor.get_gpu_temperature()
                    memory_usage = monitor.get_memory_usage()
                    
                    # ディスプレイに表示
                    display.show_system_info(cpu_temp, cpu_usage, gpu_temp, memory_usage)
                    
                    # コンソールにも表示
                    print(f"\rCPU: {cpu_temp:.1f}°C ({cpu_usage:.1f}%) | "
                          f"GPU: {gpu_temp:.1f}°C | RAM: {memory_usage:.1f}%", end='')
                    
                    time.sleep(args.interval)
                    
            except KeyboardInterrupt:
                print("\n\n🛑 モニタリングを停止しました")
                
        elif args.mode == 'custom':
            # カスタムテキストモード
            if not args.text:
                print("❌ カスタムテキストが指定されていません")
                return 1
                
            print(f"📝 カスタムテキストを表示します: {args.text}")
            display.show_custom_text(args.text)
            
        elif args.mode == 'image':
            # 画像表示モード
            if not args.image:
                print("❌ 画像ファイルパスが指定されていません")
                return 1
                
            image_path = Path(args.image)
            if not image_path.exists():
                print(f"❌ 画像ファイルが見つかりません: {args.image}")
                return 1
                
            print(f"🖼️ 画像を表示します: {args.image}")
            display.show_image(str(image_path))
        
        return 0
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1
    finally:
        try:
            display.cleanup()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
