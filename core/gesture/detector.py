
"""
手势检测核心（实现Mediapipe摄像头检测+手势转指令）
"""
import cv2
import mediapipe as mp
from core.gesture.signal import convert_gesture_to_command  # 手势转指令


class GestureDetector:
    def __init__(self, current_command):
        """
        初始化：关联全局指令字典
        :param current_command: 共享的手势指令（传给WebSocket/音乐播放器）
        """
        # 初始化Mediapipe手部检测


    def run(self):
        """
        核心运行逻辑
        流程：读取摄像头帧 → 检测手部 → 转指令 → 更新全局指令
        """
