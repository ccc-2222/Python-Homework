
"""
手势→播放器指令转换（根据手部关键点判断手势）
支持指令：play_pause（播放/暂停）、next（下一首）、prev（上一首）、volume_up（音量+）、volume_down（音量-）
"""
import math


def convert_gesture_to_command(hand_landmarks):
    """
    核心转换逻辑
    :param hand_landmarks: Mediapipe检测到的手部关键点对象
    :return: (指令字符串, 置信度0-1)
    """
