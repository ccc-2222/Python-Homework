
"""
手势→播放器指令转换（根据手部关键点判断手势）
支持指令：play_pause（播放/暂停）、next（下一首）、prev（上一首）、volume_up（音量+）、volume_down（音量-）
"""
import math


def convert_gesture_to_command(hand_landmarks):
    """
    核心转换逻辑
    :param hand_landmarks: Mediapipe检测到的手部关键点对象
    :return: (指令字符串, 置信度0-1, 手指数目)
    """
    if not hand_landmarks:
        return None, 0.0, 0

    # 获取所有关键点坐标
    landmarks = hand_landmarks.landmark
    
    # 统计伸出的手指
    # 食指(8), 中指(12), 无名指(16), 小指(20) 通过y坐标判断（指尖在指关节上方为伸出，注意y轴向下增加）
    fingers_up = []
    
    # 食指 (8 Tip vs 6 PIP)
    fingers_up.append(1 if landmarks[8].y < landmarks[6].y else 0)
    # 中指 (12 Tip vs 10 PIP)
    fingers_up.append(1 if landmarks[12].y < landmarks[10].y else 0)
    # 无名指 (16 Tip vs 14 PIP)
    fingers_up.append(1 if landmarks[16].y < landmarks[14].y else 0)
    # 小指 (20 Tip vs 18 PIP)
    fingers_up.append(1 if landmarks[20].y < landmarks[18].y else 0)
    
    # 大拇指判断逻辑 (4 Tip vs 3 IP)
    # 简单判断：指尖到各指根部平均中心(近似掌心)的距离 > 指关节到该中心的距离
    # 使用中指根部(9)作为参考点比较稳定
    dist_thumb_tip = math.hypot(landmarks[4].x - landmarks[9].x, landmarks[4].y - landmarks[9].y)
    dist_thumb_ip = math.hypot(landmarks[3].x - landmarks[9].x, landmarks[3].y - landmarks[9].y)
    
    # 如果Tip比IP离手掌更远，视为伸出
    if dist_thumb_tip > dist_thumb_ip:
        fingers_up.append(1)
    else:
        fingers_up.append(0)
    
    # 计算伸出指总数
    total_fingers = sum(fingers_up)
    
    command = None
    confidence = 0.9 # 默认置信度

    # 0根手指 -> pause
    if total_fingers == 0:
        command = "pause"
    # 1根手指 -> next
    elif total_fingers == 1:
        command = "next"
    # 2根手指 -> prev
    elif total_fingers == 2:
        command = "prev"
    # 3根手指 -> volume_up
    elif total_fingers == 3:
        command = "volume_up"
    # 4根手指 -> volume_down
    elif total_fingers == 4:
        command = "volume_down"
    # 5根手指 -> play
    elif total_fingers == 5:
        command = "play"
    else:
        confidence = 0.0
        
    return command, confidence, total_fingers
