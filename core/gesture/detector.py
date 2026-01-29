"""
手势检测核心（实现Mediapipe摄像头检测+手势转指令）
"""
import cv2
import mediapipe as mp
import time
from core.gesture.signal import convert_gesture_to_command  # 手势转指令
from core.utils.shared_frame import frame_buffer # 引入共享帧缓冲区


class GestureDetector:
    def __init__(self, current_command):
        """
        初始化：关联全局指令字典
        :param current_command: 共享的手势指令（传给WebSocket/音乐播放器）
        """
        self.current_command = current_command
        
        # 初始化Mediapipe手部检测
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # 冷却控制
        self.last_trigger_time = 0
        
        # 状态防抖相关
        self.potential_command = None    # 当前正在检测但未确认的指令
        self.stable_start_time = 0       # 潜在指令开始保持的时间
        self.last_triggered_cmd = None   # 上一次成功触发的指令
        self.display_command = "None"    # UI显示的指令

    def run(self):
        """
        核心运行逻辑
        流程：读取摄像头帧 → 检测手部 → 转指令 → 更新全局指令
        """
        cap = cv2.VideoCapture(0)
        print("摄像头已启动，按 'q' 键退出...")

        while cap.isOpened():
            success, img = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # 图像预处理
            img = cv2.flip(img, 1)  # 镜像翻转，符合直觉
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 手部检测
            results = self.hands.process(img_rgb)
            
            # 自动重置指令为idle（脉冲复位逻辑）
            # 只有当置信度不为1.0（非人工/Web端指令）时，才由此处重置
            # Web端指令由WebSocket Server自行管理复位
            if self.current_command['confidence'] != 1.0:
                if self.current_command['command'] != 'idle' and (time.time() - self.last_trigger_time > 0.2):
                    self.current_command['command'] = 'idle'
                    self.current_command['confidence'] = 0.0

            # 当前帧检测到的原始手势
            current_raw_cmd = None
            current_conf = 0.0
            current_fingers = 0

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    current_raw_cmd, current_conf, current_fingers = convert_gesture_to_command(hand_landmarks)
            
            # ---------------------- 防抖逻辑 ----------------------
            # 如果当前检测到的原始指令与“潜在指令”一致
            if current_raw_cmd == self.potential_command:
                # 检查保持时间是否超过阈值 (0.5秒)
                if (time.time() - self.stable_start_time) > 0.5:
                    # 只有当这是新指令（不同于上次触发的）时才触发
                    if current_raw_cmd != self.last_triggered_cmd:
                        # 1. 如果是有效指令，则触发
                        if current_raw_cmd is not None:
                            self.current_command['command'] = current_raw_cmd
                            self.current_command['confidence'] = current_conf
                            self.last_trigger_time = time.time() # 记录触发时间用于脉冲复位
                            self.display_command = current_raw_cmd # 更新UI
                            print(f"触发手势: {current_raw_cmd}, 手指: {current_fingers}")
                        
                        # 2. 更新“上次触发指令”（即便是None也要更新，以便下次能重新触发）
                        self.last_triggered_cmd = current_raw_cmd
            else:
                # 手势发生变化（包括变成了None），重置计时器
                self.potential_command = current_raw_cmd
                self.stable_start_time = time.time()

            # ---------------------- 界面显示 ----------------------
            # 显示当前是指数量
            cv2.putText(img, f"Fingers: {current_fingers}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # 显示当前有效触发的指令（一直显示）
            if self.display_command != "None":
                 cv2.putText(img, f"CMD: {self.display_command}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 将当前帧编码为 JPEG 并更新到共享缓冲区
            ret, buffer = cv2.imencode('.jpg', img)
            if ret:
                frame_buffer.update(buffer.tobytes())

            # cv2.imshow('Gesture Control', img) # 移除本地显示
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
