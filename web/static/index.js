// 手势音乐播放器前端逻辑

class GestureMusicPlayer {
    constructor() {
        this.ws = null;
        this.musicList = [];
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.loadMusicList();
        this.bindEvents();
    }

    connectWebSocket() {
        const wsStatus = document.getElementById('ws-status');
        const currentCommand = document.getElementById('current-command');
        const confidence = document.getElementById('confidence');

        try {
            this.ws = new WebSocket('ws://127.0.0.1:8765');

            this.ws.onopen = () => {
                wsStatus.textContent = '已连接';
                wsStatus.className = 'status connected';
                console.log('WebSocket连接成功');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    currentCommand.textContent = data.command || 'idle';
                    confidence.textContent = data.confidence ? data.confidence.toFixed(2) : '0.0';

                    // 根据指令更新按钮状态
                    this.updateButtonStates(data.command);
                } catch (e) {
                    console.error('解析WebSocket消息失败:', e);
                }
            };

            this.ws.onclose = () => {
                wsStatus.textContent = '未连接';
                wsStatus.className = 'status disconnected';
                console.log('WebSocket连接关闭');

                // 自动重连
                setTimeout(() => {
                    this.connectWebSocket();
                }, 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket错误:', error);
                wsStatus.textContent = '连接错误';
                wsStatus.className = 'status disconnected';
            };

        } catch (e) {
            console.error('创建WebSocket连接失败:', e);
            wsStatus.textContent = '连接失败';
            wsStatus.className = 'status disconnected';
        }
    }

    loadMusicList() {
        // 从服务器获取音乐列表
        fetch('/music-list')
            .then(response => response.json())
            .then(data => {
                this.musicList = data.music_list || [];
                this.renderMusicList();
            })
            .catch(error => {
                console.error('加载音乐列表失败:', error);
                // 如果获取失败, 显示空列表
                this.renderMusicList();
            });
    }

    renderMusicList() {
        const musicListElement = document.getElementById('music-list');
        musicListElement.innerHTML = '';

        if (this.musicList.length === 0) {
            musicListElement.innerHTML = '<li>暂无音乐文件</li>';
            return;
        }

        this.musicList.forEach((music, index) => {
            const li = document.createElement('li');
            li.textContent = music;
            li.dataset.index = index;
            li.addEventListener('click', () => this.playMusic(index));
            musicListElement.appendChild(li);
        });
    }

    playMusic(index) {
        // 这里可以添加播放逻辑, 但实际播放由后端控制
        console.log('选择播放:', this.musicList[index]);
        // 移除之前的播放状态
        document.querySelectorAll('.music-list li').forEach(li => {
            li.classList.remove('playing');
        });
        // 添加当前播放状态
        const selectedLi = document.querySelector(`.music-list li[data-index="${index}"]`);
        if (selectedLi) {
            selectedLi.classList.add('playing');
        }
    }

    updateButtonStates(command) {
        // 根据当前指令更新按钮视觉状态
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
        });

        // 根据指令高亮对应按钮
        switch(command) {
            case 'play':
                document.getElementById('play-btn').classList.add('active');
                break;
            case 'pause':
                document.getElementById('pause-btn').classList.add('active');
                break;
            case 'next':
                document.getElementById('next-btn').classList.add('active');
                break;
            case 'prev':
                document.getElementById('prev-btn').classList.add('active');
                break;
            case 'volume_up':
                document.getElementById('vol-up-btn').classList.add('active');
                break;
            case 'volume_down':
                document.getElementById('vol-down-btn').classList.add('active');
                break;
        }
    }

    bindEvents() {
        // 绑定按钮点击事件(可选, 用于手动测试)
        document.getElementById('play-btn').addEventListener('click', () => this.sendCommand('play'));
        document.getElementById('pause-btn').addEventListener('click', () => this.sendCommand('pause'));
        document.getElementById('next-btn').addEventListener('click', () => this.sendCommand('next'));
        document.getElementById('prev-btn').addEventListener('click', () => this.sendCommand('prev'));
        document.getElementById('vol-up-btn').addEventListener('click', () => this.sendCommand('volume_up'));
        document.getElementById('vol-down-btn').addEventListener('click', () => this.sendCommand('volume_down'));
    }

    sendCommand(command) {
        // 发送指令到服务器（如果需要的话）
        // 注意: 实际项目中指令由手势产生, 这里仅用于测试
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            // 如果需要双向通信, 可以在这里发送
            console.log('发送指令:', command);
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new GestureMusicPlayer();
});