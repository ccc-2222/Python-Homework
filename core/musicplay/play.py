"""
音乐播放核心（Pygame实现播放/暂停/切歌/音量）
"""
import pygame
import os
import time


class MusicPlayer:
    def __init__(self, current_command):
        """
        初始化：关联全局指令，加载音乐文件
        :param current_command: 接收手势指令的字典
        """

    def play_pause(self):
        """播放/暂停（"""

    def next_song(self):
        """下一首"""

    def prev_song(self):
        """上一首"""

    def adjust_volume(self, direction):
        """调整音量（up/down"""

    def listen_command(self):
        """监听手势指令，执行对应操作"""
        print("✅ 音乐播放器开始监听手势指令")
