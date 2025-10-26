#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NZXT Kraken ハードウェア制御クラス
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any

class NZXTController:
    """NZXT Krakenのハードウェア制御を行うクラス"""
    
    def __init__(self):
        """初期化"""
        self.device_paths = [
            # Windowsでの一般的なNZXTデバイスパス
            r"C:\Program Files\NZXT\NZXT CAM\NZXT CAM.exe",
            r"C:\Program Files (x86)\NZXT\NZXT CAM\NZXT CAM.exe"
        ]
        self.cam_running = False
        self.device_info = {}
        
    def is_available(self) -> bool:
        """NZXT Krakenが利用可能かチェック"""
        try:
            # NZXT CAMプロセスが実行中かチェック
            self.cam_running = self._check_cam_process()
            
            # デバイス情報を取得
            self.device_info = self._get_device_info()
            
            return len(self.device_info) > 0
            
        except Exception as e:
            print(f"デバイス検出エラー: {e}")
            return False
    
    def _check_cam_process(self) -> bool:
        """NZXT CAMプロセスが実行中かチェック"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq "NZXT CAM.exe"'],
                capture_output=True, text=True, shell=True
            )
            return "NZXT CAM.exe" in result.stdout
        except:
            return False
    
    def _get_device_info(self) -> Dict[str, Any]:
        """接続されているNZXTデバイスの情報を取得"""
        devices = {}
        
        try:
            # WMIを使用してUSBデバイスを検索
            result = subprocess.run(
                ['wmic', 'path', 'Win32_USBHub', 'get', 'DeviceID,Description'],
                capture_output=True, text=True, shell=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # ヘッダーをスキップ
                    if 'NZXT' in line or 'Kraken' in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            device_id = parts[0]
                            description = ' '.join(parts[1:])
                            devices[device_id] = {
                                'description': description,
                                'type': 'Kraken',
                                'connected': True
                            }
            
        except Exception as e:
            print(f"デバイス情報取得エラー: {e}")
        
        return devices
    
    def get_device_status(self) -> Dict[str, Any]:
        """デバイスの現在の状態を取得"""
        if not self.device_info:
            return {}
        
        status = {}
        for device_id, info in self.device_info.items():
            status[device_id] = {
                **info,
                'cam_running': self.cam_running,
                'timestamp': time.time()
            }
        
        return status
    
    def start_cam_if_needed(self) -> bool:
        """必要に応じてNZXT CAMを起動"""
        if self.cam_running:
            return True
        
        try:
            for path in self.device_paths:
                if Path(path).exists():
                    subprocess.Popen([path], shell=True)
                    time.sleep(5)  # 起動待機
                    self.cam_running = self._check_cam_process()
                    return self.cam_running
            
            print("NZXT CAMが見つかりません")
            return False
            
        except Exception as e:
            print(f"CAM起動エラー: {e}")
            return False
    
    def get_firmware_version(self) -> Optional[str]:
        """ファームウェアバージョンを取得"""
        try:
            # レジストリから情報を取得
            result = subprocess.run(
                ['reg', 'query', r'HKEY_LOCAL_MACHINE\SOFTWARE\NZXT\CAM', '/v', 'Version'],
                capture_output=True, text=True, shell=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Version' in line:
                        return line.split()[-1]
            
        except:
            pass
        
        return None
    
    def test_connection(self) -> bool:
        """デバイスとの接続テスト"""
        if not self.is_available():
            return False
        
        try:
            # 簡単な接続テスト
            status = self.get_device_status()
            return len(status) > 0
            
        except Exception as e:
            print(f"接続テストエラー: {e}")
            return False

if __name__ == "__main__":
    # テスト用
    controller = NZXTController()
    print("NZXT Kraken コントローラーテスト")
    print("=" * 40)
    
    if controller.is_available():
        print("✅ デバイスが検出されました")
        print(f"デバイス数: {len(controller.device_info)}")
        print(f"CAM実行中: {controller.cam_running}")
        
        status = controller.get_device_status()
        for device_id, info in status.items():
            print(f"デバイス: {device_id}")
            print(f"  説明: {info['description']}")
            print(f"  タイプ: {info['type']}")
        
        firmware = controller.get_firmware_version()
        if firmware:
            print(f"ファームウェア: {firmware}")
        
        if controller.test_connection():
            print("✅ 接続テスト成功")
        else:
            print("❌ 接続テスト失敗")
    else:
        print("❌ デバイスが検出されませんでした")
        print("NZXT CAMソフトウェアが起動しているか確認してください")
