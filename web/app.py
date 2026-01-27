"""
Flask前端服务
"""
from flask import Flask, render_template, send_from_directory, jsonify
import os

app = Flask(__name__,
            template_folder="static",
            static_folder="static")


# 路由：首页（播放器界面）
@app.route("/")
def index():
    # 读取音乐列表（传给前端显示）
    music_dir = os.path.join(os.path.dirname(__file__), "..", "music")
    if not os.path.exists(music_dir):
        music_list = []
    else:
        music_list = [f for f in os.listdir(music_dir) if f.endswith((".mp3", ".ogg", ".wav"))]
    return render_template("index.html", music_list=music_list)


# 路由：获取音乐列表JSON（供前端AJAX调用）
@app.route("/music-list")
def get_music_list():
    music_dir = os.path.join(os.path.dirname(__file__), "..", "music")
    if not os.path.exists(music_dir):
        return jsonify({"music_list": []})
    music_list = [f for f in os.listdir(music_dir) if f.endswith((".mp3", ".ogg", ".wav"))]
    return jsonify({"music_list": music_list})


# 路由：提供音乐文件（前端播放用）
@app.route("/music/<filename>")
def get_music(filename):
    music_dir = os.path.join(os.path.dirname(__file__), "..", "music")
    return send_from_directory(music_dir, filename)


def run_flask_app():
    """供main.py调用的启动函数"""
    app.run(host="127.0.0.1", port=5000, debug=True)  # debug模式方便开发


if __name__ == "__main__":
    run_flask_app()
