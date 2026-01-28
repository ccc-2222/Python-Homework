"""
主程序：添加全流程异常捕获，定位启动错误
"""
import threading
import time
import sys

print(f"当前Python路径：{sys.path}")

def main():
    print("=== 手势音乐播放器启动（带异常捕获） ===")
    current_command = {"command": "idle", "confidence": 0.0}

    # 1. 尝试导入所有模块（捕获导入错误）
    try:
        from core.gesture.detector import GestureDetector
        from core.musicplay.play import MusicPlayer
        from core.websocket.server import WebSocketServer
        from web.app import run_flask_app
        print("✅ 所有模块导入成功")
    except ImportError as e:
        print(f"❌ 模块导入失败：{e}")
        return
    except Exception as e:
        print(f"❌ 导入模块时发生未知错误：{e}")
        return

    # 2. 启动Flask前端（捕获启动错误）
    try:
        flask_thread = threading.Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        print("✅ Flask前端：http://127.0.0.1:5000")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Flask启动失败：{e}")

    # 3. 启动WebSocket服务（捕获启动错误）
    try:
        ws_server = WebSocketServer(current_command)
        ws_thread = threading.Thread(target=ws_server.run, daemon=True)
        ws_thread.start()
        print("✅ WebSocket服务：ws://127.0.0.1:8765")
    except Exception as e:
        print(f"❌ WebSocket启动失败：{e}")

    # 4. 启动音乐播放器（捕获启动错误）
    try:
        music_player = MusicPlayer(current_command)
        player_thread = threading.Thread(target=music_player.listen_command, daemon=True)
        player_thread.start()
        print("✅ 音乐播放器已启动")
    except Exception as e:
        print(f"❌ 音乐播放器启动失败：{e}")
        return

    # 5. 启动手势识别（捕获启动错误）
    try:
        gesture_detector = GestureDetector(current_command)
        print("✅ 手势识别启动（摄像头已打开）")
        gesture_detector.run()
    except Exception as e:
        print(f"❌ 手势识别启动失败：{e}")
    except KeyboardInterrupt:
        print("\n⚠️  手动终止程序")
    finally:
        print("=== 程序已关闭 ===")

if __name__ == "__main__":
    # 捕获main函数的所有异常
    try:
        main()
    except Exception as e:
        print(f"❌ 主程序运行失败：{e}")