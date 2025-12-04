# 要先安装 pip install flask

import os
from flask import Flask, request, send_from_directory, render_template_string
import socket

# --- 配置 ---
# 设置共享文件夹路径
SHARE_FOLDER = r"E:\code\back\logs\2025-12-02T00-00-31_git10m_train_2\checkpoints"
# 设置端口号
PORT = 8000

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = SHARE_FOLDER

# --- 简单的 HTML 模板 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>局域网文件共享</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 20px auto; padding: 0 10px; }
        h1 { color: #333; }
        .upload-section { background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .file-list { list-style: none; padding: 0; }
        .file-list li { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .file-list li:last-child { border-bottom: none; }
        a { text-decoration: none; color: #007bff; font-weight: bold; }
        .btn { background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #218838; }
        .size { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>📂 局域网文件共享</h1>
    
    <div class="upload-section">
        <h3>上传文件</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit" class="btn">上传</button>
        </form>
    </div>

    <h3>文件列表 ({{ files|length }})</h3>
    <ul class="file-list">
        {% for file in files %}
        <li>
            <span>{{ file.name }}</span>
            <div>
                <span class="size">{{ file.size }}</span>
                <a href="/download/{{ file.name }}">下载 ↓</a>
            </div>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
"""

def get_file_size(path):
    """获取人类可读的文件大小"""
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@app.route('/')
def index():
    files = []
    # 遍历目录下的文件
    for filename in os.listdir(SHARE_FOLDER):
        path = os.path.join(SHARE_FOLDER, filename)
        if os.path.isfile(path):
            files.append({
                'name': filename,
                'size': get_file_size(path)
            })
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(SHARE_FOLDER, filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '无文件部分', 400
    file = request.files['file']
    if file.filename == '':
        return '未选择文件', 400
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return '<script>alert("上传成功!"); window.location.href="/";</script>'

def get_ip_address():
    """获取本机局域网IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 不需要真的连接，只是为了获取IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    local_ip = get_ip_address()
    print(f"--- 服务已启动 ---")
    print(f"共享目录: {SHARE_FOLDER}")
    print(f"请在局域网设备浏览器输入: http://{local_ip}:{PORT}")
    print(f"------------------")
    # host='0.0.0.0' 允许外部访问
    app.run(host='0.0.0.0', port=PORT, debug=False)