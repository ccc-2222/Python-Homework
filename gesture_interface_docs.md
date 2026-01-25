# Gesture 模块接口文档

`core.gesture` 是本项目的手势识别核心包，负责从摄像头捕获图像、识别手势并输出控制指令。

## 1. 模块功能
该模块封装了 MediaPipe Hands 检测逻辑，提供一个可以独立运行的检测器类 `GestureDetector`。它通过修改传入的共享字典来实现与其他模块（如播放器、WebSocket 服务）的通信。

## 2. 核心指令定义 (Command Protocol)

模块将检测到的手部动作转换为以下标准指令字符串。其他消费者模块应依据此协议编写相应的响应逻辑。

| 手指数量 | 指令代码 (`command`) | 语义描述 | 触发机制 |
| :--- | :--- | :--- | :--- |
| **0指 (握拳)** | `pause` | 暂停 | 保持 0.3s 稳定触发 |
| **1指** | `next` | 下一首 | 保持 0.3s 稳定触发 |
| **2指** | `prev` | 上一首 | 保持 0.3s 稳定触发 |
| **3指** | `volume_up` | 音量 + | 保持 0.3s 稳定触发 |
| **4指** | `volume_down` | 音量 - | 保持 0.3s 稳定触发 |
| **5指 (张开)** | `play` | 播放 | 保持 0.3s 稳定触发 |
| **(其他)** | `idle` | 空闲/无指令 | 默认状态或复位状态 |

> **防抖说明**: 为了防止误触，模块内部实现了状态防抖。只有当手势连续保持稳定超过 **0.3秒**，且产生的指令与上一次触发的指令不同时，共享变量才会被更新。

## 3. Python API 接口

### 类: `core.gesture.detector.GestureDetector`

#### 初始化
```python
def __init__(self, current_command: dict)
```

**参数**:
*   `current_command` (dict): 一个由主线程创建的共享字典，用于存储最新的指令状态。

#### 运行
```python
def run(self)
```
启动摄像头捕获循环。该方法是阻塞的，建议在独立线程中运行。
*   按 `q` 键可退出循环（仅限有 GUI 窗口测试时）。

## 4. 输出数据结构 (Shared State)

`GestureDetector` 会实时修改传入的 `current_command` 字典。消费者模块应轮询此字典。

**字典结构**:
```python
{
    "command": str,      # 当前触发的指令 (见第2节表)
    "confidence": float  # 置信度 (0.0 - 1.0)
}
```

**消费者集成示例**:

```python
from core.gesture.detector import GestureDetector
import threading

# 1. 定义共享变量
shared_state = {"command": "idle", "confidence": 0.0}

# 2. 启动检测器 (建议在独立线程中运行，因为它包含死循环)
detector = GestureDetector(shared_state)
# detector.run() # 这会阻塞主线程

# 3. 在消费端读取
def consumer_logic():
    last_cmd = None
    while True:
        current_cmd = shared_state['command']
        if current_cmd != "idle" and current_cmd != last_cmd:
            print(f"收到新指令: {current_cmd}")
            last_cmd = current_cmd
        # ...
```
