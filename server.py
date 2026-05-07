#!/usr/bin/env python3
"""
飞书课程报告生成服务 - 服务器部署版本
提供HTTP API接口，支持手动触发和定时任务
"""

from flask import Flask, jsonify, send_from_directory
import subprocess
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)

# 配置
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
GENERATE_SCRIPT = os.path.join(os.path.dirname(__file__), 'generate.py')
UPDATE_LINKS_SCRIPT = os.path.join(os.path.dirname(__file__), 'generate_report_links.py')

# 确保reports目录存在
os.makedirs(REPORTS_DIR, exist_ok=True)

# 全局状态
last_generation = {
    'time': None,
    'status': 'idle',
    'message': ''
}

def generate_reports():
    """执行报告生成流程"""
    global last_generation

    try:
        last_generation['status'] = 'running'
        last_generation['time'] = datetime.now().isoformat()

        # 1. 生成HTML报告
        print(f"[{datetime.now()}] 开始生成报告...")
        result1 = subprocess.run(
            ['python', GENERATE_SCRIPT],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result1.returncode != 0:
            raise Exception(f"生成报告失败: {result1.stderr}")

        # 2. 回填飞书链接
        print(f"[{datetime.now()}] 开始回填链接...")
        result2 = subprocess.run(
            ['python', UPDATE_LINKS_SCRIPT],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result2.returncode != 0:
            raise Exception(f"回填链接失败: {result2.stderr}")

        last_generation['status'] = 'success'
        last_generation['message'] = '报告生成成功'
        print(f"[{datetime.now()}] 报告生成完成")

    except Exception as e:
        last_generation['status'] = 'error'
        last_generation['message'] = str(e)
        print(f"[{datetime.now()}] 错误: {str(e)}")

def scheduled_task():
    """定时任务：每15分钟执行一次"""
    while True:
        try:
            generate_reports()
        except Exception as e:
            print(f"定时任务执行失败: {str(e)}")

        # 等待15分钟
        time.sleep(15 * 60)

@app.route('/')
def index():
    """首页"""
    return '''
    <html>
    <head>
        <meta charset="utf-8">
        <title>飞书课程报告生成服务</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .status { padding: 15px; border-radius: 8px; margin: 20px 0; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .running { background: #fff3cd; color: #856404; }
            .idle { background: #d1ecf1; color: #0c5460; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>飞书课程报告生成服务</h1>
        <p>服务运行中，每15分钟自动生成报告</p>

        <div>
            <button onclick="triggerGeneration()">立即生成报告</button>
            <button onclick="checkStatus()">刷新状态</button>
        </div>

        <div id="status"></div>

        <h3>API接口</h3>
        <ul>
            <li><code>GET /</code> - 服务首页</li>
            <li><code>POST /api/generate</code> - 手动触发生成</li>
            <li><code>GET /api/status</code> - 查看生成状态</li>
            <li><code>GET /reports/{record_id}.html</code> - 访问报告</li>
        </ul>

        <script>
            function triggerGeneration() {
                fetch('/api/generate', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        checkStatus();
                    });
            }

            function checkStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        const statusDiv = document.getElementById('status');
                        statusDiv.className = 'status ' + data.status;
                        statusDiv.innerHTML = `
                            <strong>状态:</strong> ${data.status}<br>
                            <strong>最后执行:</strong> ${data.last_time || '未执行'}<br>
                            <strong>消息:</strong> ${data.message || '无'}
                        `;
                    });
            }

            // 页面加载时检查状态
            checkStatus();

            // 每30秒自动刷新状态
            setInterval(checkStatus, 30000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API: 手动触发生成"""
    if last_generation['status'] == 'running':
        return jsonify({
            'success': False,
            'message': '报告生成正在进行中，请稍后再试'
        }), 429

    # 在后台线程执行
    thread = threading.Thread(target=generate_reports)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': '报告生成已启动'
    })

@app.route('/api/status')
def api_status():
    """API: 查看生成状态"""
    return jsonify({
        'status': last_generation['status'],
        'last_time': last_generation['time'],
        'message': last_generation['message']
    })

@app.route('/reports/<path:filename>')
def serve_report(filename):
    """提供报告文件访问"""
    return send_from_directory(REPORTS_DIR, filename)

if __name__ == '__main__':
    # 启动定时任务线程
    scheduler = threading.Thread(target=scheduled_task)
    scheduler.daemon = True
    scheduler.start()

    print("=" * 50)
    print("飞书课程报告生成服务已启动")
    print("=" * 50)
    print("访问地址: http://0.0.0.0:5000")
    print("定时任务: 每15分钟自动生成")
    print("=" * 50)

    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=False)
