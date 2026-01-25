"""
手势识别独立测试脚本
"""
import sys
import os

# 将当前目录添加到系统路径，确保能导入core模块
sys.path.append(os.getcwd())

from core.gesture.detector import GestureDetector

def test_gesture():
    # 1. 定义模拟的共享指令变量
    # 在主程序中，这个变量会被多个线程共享
    shared_command = {"command": "idle", "confidence": 0.0}

    print("=== 手势识别模块测试模式 ===")
    print("功能说明：")
    print("  0根手指 -> pause (暂停)")
    print("  1根手指 -> next (下一首)")
    print("  2根手指 -> prev (上一首)")
    print("  3根手指 -> volume_up (音量+)")
    print("  4根手指 -> volume_down (音量-)")
    print("  5根手指 -> play (播放)")
    print("--------------------------------")
    print("正在启动摄像头... (按 'q' 键退出)")

    # 2. 初始化检测器
    detector = GestureDetector(shared_command)

    # 3. 运行检测循环 (这是一个阻塞调用)
    # 检测器内部会更新 shared_command，并在控制台打印触发的指令
    detector.run()

if __name__ == "__main__":
    try:
        test_gesture()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保你安装了必要的依赖: pip install opencv-python mediapipe")
    except Exception as e:
        print(f"运行时错误: {e}")
