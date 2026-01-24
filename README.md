# 用python实现手势识别音乐播放器

框架如下,根据个人实现内容差异可增删个人版块

├── requirements.txt   # 依赖清单示例，方便统一环境
├── main.py            # 项目入口，启动Flask+WebSocket+手势识别
├── core/              # 核心模块（手势识别+音乐播放）
│   ├── __init__.py    # 整个该模块初始化
│   ├── gesture/       # 手势识别模块
│   │   ├── __init__.py
│   │   ├── detector.py # 手势检测
│   │   └── signal.py # 手势→指令
│   ├── player/        # 音乐播放模块
│   │   ├── __init__.py
│   │   └── music_player.py # Pygame音频控制
│   └── websocket/     # 前后端通信
│       ├── __init__.py
│       └── server.py  # WebSocket服务，来关联手势指令和前端
└── web/               # 前端模块
    ├── __init__.py
    ├── app.py         # Flask Web服务
    ├── static/        # CSS/JS/音乐文件
    │   ├── index.css
    │   ├── index.js
    │   ├── index.html
    │   └── music/     # 存放测试音乐

