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
    fingers_up = []
    # 指尖在指关节上方为伸出 -> 改为：指尖距离手腕(0)的距离 > 指关节距离手腕(0)的距离
    # 这样可以适应手稍微倾斜的情况，不仅限于垂直向上
    wrist = landmarks[0]
    
    def get_dist(p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)
    
    # 食指 (8 Tip vs 6 PIP)
    fingers_up.append(1 if get_dist(landmarks[8], wrist) > get_dist(landmarks[6], wrist) else 0)
    # 中指 (12 Tip vs 10 PIP)
    fingers_up.append(1 if get_dist(landmarks[12], wrist) > get_dist(landmarks[10], wrist) else 0)
    # 无名指 (16 Tip vs 14 PIP)
    fingers_up.append(1 if get_dist(landmarks[16], wrist) > get_dist(landmarks[14], wrist) else 0)
    # 小指 (20 Tip vs 18 PIP)
    fingers_up.append(1 if get_dist(landmarks[20], wrist) > get_dist(landmarks[18], wrist) else 0)
    
    # 大拇指判断逻辑 (4 Tip vs 3 IP)
    # 简单判断：指尖到各指根部平均中心(近似掌心)的距离 > 指关节到该中心的距离
    # 使用中指根部(9)作为参考点比较稳定
    dist_thumb_tip = get_dist(landmarks[4], landmarks[9])
    dist_thumb_ip = get_dist(landmarks[3], landmarks[9])
    
    # 辅助判断1：大拇指是否外展（防止手背对摄像头时误判）
    # 大拇指张开时，指尖(4)到小指根部(17)的距离 通常明显大于 食指根部(5)到小指根部(17)的距离
    is_thumb_far_from_pinky = get_dist(landmarks[4], landmarks[17]) > get_dist(landmarks[5], landmarks[17])
    
    # 辅助判断2：大拇指是否远离食指（防止侧对摄像头时误判）
    # 大拇指伸开时，指尖(4)到食指根部(5)的距离 应该大于 食指第一指节长度(5-6)
    is_thumb_far_from_index = get_dist(landmarks[4], landmarks[5]) > get_dist(landmarks[5], landmarks[6])

    # 如果Tip比IP离手掌更远(且超过一定阈值)，并且满足外展条件，视为伸出
    if dist_thumb_tip > dist_thumb_ip * 1.05 and is_thumb_far_from_pinky and is_thumb_far_from_index:
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
