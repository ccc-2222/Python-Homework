"""
Flask前端服务：适配根目录music文件夹
"""
from flask import Flask, render_template, send_from_directory, jsonify
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "web", "static"),
    static_folder=os.path.join(BASE_DIR, "web", "static")
)

# 首页路由：读取根目录music的音乐列表
@app.route("/")
def index():
    music_dir = os.path.join(BASE_DIR, "music")
    music_list = [f for f in os.listdir(music_dir) if f.endswith(".mp3")]
    return render_template("index.html", music_list=music_list)

# 音乐文件路由：提供根目录music的音频
@app.route("/music/<filename>")
def get_music(filename):
    music_dir = os.path.join(BASE_DIR, "music")
    return send_from_directory(music_dir, filename)

# 音乐列表路由：返回JSON格式的音乐列表
@app.route("/music-list")
def music_list():
    music_dir = os.path.join(BASE_DIR, "music")
    if not os.path.exists(music_dir):
        return jsonify({"music_list": []})

    music_list = [f for f in os.listdir(music_dir) if f.endswith(".mp3")]
    return jsonify({"music_list": music_list})

# 当前播放音乐路由：返回当前播放音乐的信息
@app.route("/current-music")
def current_music():
    from core.musicplay.play import MusicPlayer
    # 假设 MusicPlayer 实例已初始化为 `player`
    current_music = player.get_current_music() if 'player' in globals() else None
    return jsonify({"current_music": current_music})

# 视频流路由：返回 MJPEG 流
@app.route("/video_feed")
def video_feed():
    from core.utils.shared_frame import frame_buffer
    
    def generate():
        while True:
            frame = frame_buffer.get()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # 如果没有帧（摄像头未启动或初始化中），可以返回空或者等待
                import time
                time.sleep(0.1)

    return app.response_class(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask_app():
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    run_flask_app()