gesture_music_player/ # 项目根目录
requirements.txt # 依赖清单（统一开发环境）
main.py # 项目入口：启动 Flask+WebSocket + 手势识别
core/ # 核心模块（手势识别 + 音乐播放 + 通信）
    init.py # core 模块初始化
    gesture/ # 手势识别子模块
        init.py
        detector.py # Mediapipe 手部检测核心
        signal.py # 手势关键点→播放器指令转换
    player/ # 音乐播放子模块
        init.py
        music_player.py # Pygame 音频控制（播放 / 暂停 / 切歌
    websocket/ # 前后端通信子模块
        init.py
        server.py # WebSocket 服务（转发手势指令到前端）
    web/ # Flask 前端模块
        init.py # web 
        app.py # Flask Web 服务（提供网页界面）
        static/ # 静态资源目录
            index.css # 播放器界面样式
            index.js # 前端交互 + WebSocket 监听
            index.html # 播放器主页面
        music/ # 测试音乐存放目录

