"""
手势控制音乐播放器测试文件
适配你的项目结构（core/gesture/detector.py + core/musicplay/play.py）
"""
import threading
import sys
import os
import pygame

# 确保项目根目录在Python路径中（保证能导入core下的模块）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 修正模块导入路径（匹配你的项目结构）
from core.gesture.detector import GestureDetector
from core.musicplay.play import MusicPlayer

def main():
    # 多线程共享的指令字典（手势识别→音乐播放的通信载体）
    shared_command = {
        "command": "idle",
        "confidence": 0.0
    }

    # 初始化音乐播放器
    music_player = MusicPlayer(shared_command)
    
    # 启动音乐播放的指令监听线程（后台运行）
    player_thread = threading.Thread(target=music_player.listen_command, daemon=True)
    player_thread.start()
    print("✅ 音乐播放器线程已启动")

    # 启动手势识别（主线程运行）
    gesture_detector = GestureDetector(shared_command)
    try:
        gesture_detector.run()
    except KeyboardInterrupt:
        print("\n⚠️  手动中断程序")
    finally:
        # 清理资源
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("✅ 测试程序已退出")

if __name__ == "__main__":
    print("="*50)
    print("📢 手势控制音乐测试（仅核心模块）")
    print("手势对应指令：0指=暂停 | 1指=下一首 | 2指=上一首 | 3指=音量+ | 4指=音量- | 5指=播放")
    print("按摄像头窗口的 'q' 键退出")
    print("="*50 + "\n")

    # 检查依赖
    try:
        import cv2
        import mediapipe
    except ImportError as e:
        print(f"❌ 缺少依赖：{e.name}，请执行：pip install opencv-python mediapipe pygame")
        sys.exit(1)

    main()