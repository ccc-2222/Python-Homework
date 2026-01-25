"""
功能：启动Flask前端、WebSocket服务、手势识别、音乐播放
"""
import threading
import time
from core.gesture.detector import GestureDetector  # 手势模块
from core.musicplay.play import MusicPlayer  # 音乐模块
from core.websocket.server import WebSocketServer  # 前后端通信模块
from web.app import run_flask_app  # 前端模块

# 全局变量：存储当前手势指令（供所有模块共享）
current_command = {"command": "idle", "confidence": 0.0}


def main():
    print("=== 手势识别音乐播放器启动中 ===")

    # 1. 启动Flask前端（子线程，不阻塞）
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    print("✅ Flask前端已启动：http://127.0.0.1:5000")
    time.sleep(2)  # 等待前端服务加载

    # 2. 启动WebSocket服务（子线程，转发手势指令）
    ws_server = WebSocketServer(current_command)
    ws_thread = threading.Thread(target=ws_server.run, daemon=True)
    ws_thread.start()
    print("✅ WebSocket服务已启动：ws://127.0.0.1:8765")

    # 3. 启动音乐播放器（子线程，监听指令）
    music_player = MusicPlayer(current_command)
    player_thread = threading.Thread(target=music_player.listen_command, daemon=True)
    player_thread.start()
    print("✅ 音乐播放器已启动")

    # 4. 启动手势识别（主线程，摄像头实时检测）
    gesture_detector = GestureDetector(current_command)
    try:
        print("✅ 手势识别模块启动（请打开摄像头）")
        gesture_detector.run()  # cl需实现该方法
    except KeyboardInterrupt:
        print("\n⚠️  程序已手动终止")
    finally:
        print("=== 播放器已关闭 ===")


if __name__ == "__main__":
    main()