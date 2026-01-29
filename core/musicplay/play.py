"""
音乐播放模块：适配根目录music文件夹
"""
import os
import time
import pygame
from typing import Dict

MUSIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "music"
)
SUPPORT_FORMATS = (".mp3", ".ogg", ".wav")

class MusicPlayer:
    def __init__(self, shared_command: Dict[str, any]):
        self.shared_command = shared_command
        pygame.mixer.init()
        self.music_list = self._load_music_list()
        self.current_index = 0
        self.is_playing = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)

    def _load_music_list(self) -> list:
        """加载根目录music文件夹的音频"""
        if not os.path.exists(MUSIC_DIR):
            os.makedirs(MUSIC_DIR)
            print(f"⚠️  根目录music文件夹不存在，已自动创建")
            return []
        music_files = [
            os.path.join(MUSIC_DIR, f)
            for f in os.listdir(MUSIC_DIR)
            if f.lower().endswith(SUPPORT_FORMATS)
        ]
        if not music_files:
            print(f"⚠️  根目录music文件夹无可用音频（支持：{SUPPORT_FORMATS}）")
        else:
            print(f"✅ 加载到 {len(music_files)} 首音乐：{[os.path.basename(f) for f in music_files]}")
        return music_files

    def _play_current_music(self):
        if not self.music_list:
            return
        try:
            pygame.mixer.music.load(self.music_list[self.current_index])
            pygame.mixer.music.play()
            self.is_playing = True
            current_song = os.path.basename(self.music_list[self.current_index])
            # 更新共享状态中的当前音乐
            self.shared_command['current_music'] = current_song
            print(f"🎵 播放：{current_song}")
        except Exception as e:
            print(f"播放失败：{e}")
            self.is_playing = False

    def _next_music(self):
        if len(self.music_list) <= 1:
            return
        self.current_index = (self.current_index + 1) % len(self.music_list)
        self._play_current_music()
        # 更新当前播放音乐的全局状态
        self.shared_command['current_music'] = self.get_current_music()

    def _prev_music(self):
        if len(self.music_list) <= 1:
            return
        self.current_index = (self.current_index - 1) % len(self.music_list)
        self._play_current_music()
        # 更新当前播放音乐的全局状态
        self.shared_command['current_music'] = self.get_current_music()

    def _adjust_volume(self, direction: str):
        if direction == "up":
            self.volume = min(1.0, self.volume + 0.1)
        elif direction == "down":
            self.volume = max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)
        print(f"🔊 音量：{round(self.volume, 1)}")

    def get_current_music(self):
        """获取当前播放的音乐名称"""
        if self.music_list and self.is_playing:
            return os.path.basename(self.music_list[self.current_index])
        return None

    def listen_command(self):
        print("🎶 音乐播放器就绪，等待手势指令...")
        last_command = "idle"
        while True:
            current_cmd = self.shared_command.get("command", "idle")
            confidence = self.shared_command.get("confidence", 0.0)

            if confidence > 0.8 and current_cmd != last_command:
                last_command = current_cmd
                if current_cmd == "play" and not self.is_playing:
                    self._play_current_music()
                elif current_cmd == "pause" and self.is_playing:
                    pygame.mixer.music.pause()
                    self.is_playing = False
                    print("⏸️  暂停")
                elif current_cmd == "next":
                    self._next_music()
                elif current_cmd == "prev":
                    self._prev_music()
                elif current_cmd == "volume_up":
                    self._adjust_volume("up")
                elif current_cmd == "volume_down":
                    self._adjust_volume("down")
            
            time.sleep(0.1)