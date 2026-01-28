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

def run_flask_app():
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    run_flask_app()