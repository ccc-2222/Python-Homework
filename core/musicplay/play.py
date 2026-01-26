"""
音乐播放模块：监听共享指令变量，执行对应的播放/暂停/切歌等操作
"""
import os
import time
import pygame
from typing import Dict

# 配置：音乐文件夹路径（可根据实际修改）
MUSIC_DIR = "./music"  # 需手动创建该文件夹并放入音频文件（mp3/ogg 等）
SUPPORT_FORMATS = (".mp3", ".ogg", ".wav")

class MusicPlayer:
    def __init__(self, shared_command: Dict[str, any]):
        # 接收主程序的共享指令变量（多线程共享）
        self.shared_command = shared_command
        # 初始化音乐播放器
        pygame.mixer.init()
        # 音乐列表 & 状态变量
        self.music_list = self._load_music_list()
        self.current_index = 0
        self.is_playing = False
        self.volume = 0.5  # 初始音量（0.0-1.0）
        pygame.mixer.music.set_volume(self.volume)

    def _load_music_list(self) -> list:
        """加载指定文件夹下的所有音频文件"""
        if not os.path.exists(MUSIC_DIR):
            os.makedirs(MUSIC_DIR)
            print(f"⚠️  音乐文件夹 {MUSIC_DIR} 不存在，已自动创建，请放入音频文件")
            return []
        # 筛选支持的音频格式
        music_files = [
            os.path.join(MUSIC_DIR, f)
            for f in os.listdir(MUSIC_DIR)
            if f.lower().endswith(SUPPORT_FORMATS)
        ]
        if not music_files:
            print(f"⚠️  音乐文件夹 {MUSIC_DIR} 中无可用音频文件（支持格式：{SUPPORT_FORMATS}）")
        return music_files

    def _play_current_music(self):
        """播放当前索引的音乐"""
        if not self.music_list:
            return
        try:
            pygame.mixer.music.load(self.music_list[self.current_index])
            pygame.mixer.music.play()
            self.is_playing = True
            print(f"🎵 正在播放：{os.path.basename(self.music_list[self.current_index])}")
        except Exception as e:
            print(f"播放失败：{e}")
            self.is_playing = False

    def _next_music(self):
        """下一首"""
        if len(self.music_list) <= 1:
            return
        self.current_index = (self.current_index + 1) % len(self.music_list)
        self._play_current_music()

    def _prev_music(self):
        """上一首"""
        if len(self.music_list) <= 1:
            return
        self.current_index = (self.current_index - 1) % len(self.music_list)
        self._play_current_music()

    def _adjust_volume(self, direction: str):
        """调节音量"""
        if direction == "up":
            self.volume = min(1.0, self.volume + 0.1)
        elif direction == "down":
            self.volume = max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)
        print(f"🔊 音量已调整至：{round(self.volume, 1)}")

    def listen_command(self):
        """监听共享指令变量（线程循环）"""
        print("🎶 音乐播放器已就绪，等待手势指令...")
        last_command = "idle"  # 记录上一次指令，避免重复执行
        while True:
            # 读取共享指令（由手势识别模块更新）
            current_cmd = self.shared_command.get("command", "idle")
            confidence = self.shared_command.get("confidence", 0.0)

            # 仅处理置信度>0.8的有效指令，且避免重复执行
            if confidence > 0.8 and current_cmd != last_command:
                last_command = current_cmd
                # 根据指令执行对应操作
                if current_cmd == "play" and not self.is_playing:
                    self._play_current_music()
                elif current_cmd == "pause" and self.is_playing:
                    pygame.mixer.music.pause()
                    self.is_playing = False
                    print("⏸️  已暂停播放")
                elif current_cmd == "next":
                    self._next_music()
                elif current_cmd == "prev":
                    self._prev_music()
                elif current_cmd == "volume_up":
                    self._adjust_volume("up")
                elif current_cmd == "volume_down":
                    self._adjust_volume("down")
            
            # 降低循环频率，减少资源占用
            time.sleep(0.1)