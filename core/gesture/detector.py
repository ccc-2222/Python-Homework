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
        # 新增：音量手势专属冷却（控制连续触发间隔）
        self.last_volume_trigger = 0
        self.volume_interval = 0.2  # 音量连续触发间隔（200ms）
        
        # 状态防抖相关
        self.potential_command = None    # 当前正在检测但未确认的指令
        self.stable_start_time = 0       # 潜在指令开始保持的时间
        self.last_triggered_cmd = None   # 上一次成功触发的指令
        self.display_command = "None"    # UI显示的指令
        self.is_running = False          # 运行控制标志

    def stop(self):
        """停止检测循环"""
        self.is_running = False

    def run(self):
        """
        核心运行逻辑
        流程：读取摄像头帧 → 检测手部 → 转指令 → 更新全局指令
        """
        self.is_running = True
        cap = cv2.VideoCapture(0)
        print("摄像头已启动...")

        while cap.isOpened() and self.is_running:
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
            
            # ---------------------- 防抖逻辑（区分音量/非音量） ----------------------
            volume_cmds = ["volume_up", "volume_down"]  # 音量指令列表
            if current_raw_cmd == self.potential_command:
                # 1. 音量手势：允许连续触发
                if current_raw_cmd in volume_cmds:
                    # 稳定0.2秒后，按间隔连续触发
                    if (time.time() - self.stable_start_time) > 0.8 and \
                       (time.time() - self.last_volume_trigger) > self.volume_interval:
                        if current_raw_cmd is not None:
                            self.current_command['command'] = current_raw_cmd
                            self.current_command['confidence'] = current_conf
                            self.last_trigger_time = time.time()
                            self.last_volume_trigger = time.time()  # 更新音量触发时间
                            self.display_command = current_raw_cmd
                            print(f"触发音量手势: {current_raw_cmd}, 手指: {current_fingers}")
                # 2. 非音量手势：保留原有防重复逻辑
                else:
                    if (time.time() - self.stable_start_time) > 0.5:
                        if current_raw_cmd != self.last_triggered_cmd:
                            if current_raw_cmd is not None:
                                self.current_command['command'] = current_raw_cmd
                                self.current_command['confidence'] = current_conf
                                self.last_trigger_time = time.time()
                                self.display_command = current_raw_cmd
                                print(f"触发手势: {current_raw_cmd}, 手指: {current_fingers}")
                            self.last_triggered_cmd = current_raw_cmd
            else:
                # 手势变化，重置状态
                self.potential_command = current_raw_cmd
                self.stable_start_time = time.time()
                if current_raw_cmd not in volume_cmds:
                    self.last_volume_trigger = 0  # 切换非音量手势时重置

            # ---------------------- 界面显示 ----------------------
            cv2.putText(img, f"Fingers: {current_fingers}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            if self.display_command != "None":
                 cv2.putText(img, f"CMD: {self.display_command}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 更新共享帧缓冲区
            ret, buffer = cv2.imencode('.jpg', img)
            if ret:
                frame_buffer.update(buffer.tobytes())

            time.sleep(0.01)
                
        cap.release()
        cv2.destroyAllWindows()