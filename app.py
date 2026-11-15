import os
import subprocess
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

# File lưu code do mày dán vào
WORKER_FILE = "worker_app.py"
worker_process = None

# Giao diện trung tâm quản lý trên Render
RENDER_DASHBOARD = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Render Code Engine</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; margin: 0; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 850px; }
        .card { background: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        h2 { color: #38bdf8; margin-top: 0; }
        textarea { width: 100%; height: 300px; background: #0f172a; color: #34d399; border: 1px solid #475569; padding: 12px; border-radius: 6px; box-sizing: border-box; font-family: monospace; font-size: 14px; }
        button { background: #0284c7; color: white; border: none; padding: 12px 20px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%; font-size: 16px; margin-top: 10px; }
        button:hover { background: #0ea5e9; }
        .btn-stop { background: #dc2626; margin-top: 10px; }
        .btn-stop:hover { background: #ef4444; }
        .status { padding: 10px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; text-align: center; }
        .running { background: #065f46; color: #34d399; }
        .stopped { background: #7f1d1d; color: #fca5a5; }
        .info-box { background: #0f172a; padding: 15px; border-radius: 6px; border: 1px solid #334155; margin-top: 15px; }
        a { color: #38bdf8; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>☁️ Render Central Engine</h2>
            
            <div class="status {{ 'running' if is_running else 'stopped' }}">
                Trạng thái tiến trình cổng 5000: {{ "ĐANG CHẠY 🟢" if is_running else "ĐÃ DỪNG 🔴" }}
            </div>

            <form action="/deploy" method="POST">
                <label style="color: #94a3b8; font-size: 13px;">Dán mã nguồn Python (Flask) của mày vào đây:</label><br><br>
                <textarea name="code" required>{{ code_content }}</textarea>
                <button type="submit">🚀 Lưu Code & Chạy trên Cổng 5000</button>
            </form>

            {% if is_running %}
            <div class="info-box">
                <p>⚡ Tiến trình web mới đã được khởi chạy ngầm trên <strong>cổng 5000</strong> bên trong Render.</p>
                <form action="/stop" method="POST">
                    <button type="submit" class="btn-stop">🛑 Dừng Tiến Trình Cổng 5000</button>
                </form>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    global worker_process
    is_running = worker_process is not None and worker_process.poll() is None
    
    code_content = ""
    if os.path.exists(WORKER_FILE):
        with open(WORKER_FILE, "r", encoding="utf-8") as f:
            code_content = f.read()
    else:
        # Code mẫu mặc định chạy trên cổng 5000
        code_content = """from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\no\ndef home():\n    return '<h1>✨ Chào từ Web chạy trên cổng 5000!</h1>'\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)"""

    return render_template_string(RENDER_DASHBOARD, is_running=is_running, code_content=code_content)

@app.route('/deploy', methods=['POST'])
def deploy():
    global worker_process
    code = request.form.get('code')
    
    # 1. Lưu code mới vào file worker
    with open(WORKER_FILE, "w", encoding="utf-8") as f:
        f.write(code)
        
    # 2. Nếu đang chạy tiến trình cũ thì tắt đi
    if worker_process and worker_process.poll() is None:
        worker_process.terminate()
        worker_process.wait()
        
    # 3. Khởi chạy tiến trình mới trỏ vào cổng 5000
    worker_process = subprocess.Popen(["python", WORKER_FILE])
    
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    global worker_process
    if worker_process and worker_process.poll() is None:
        worker_process.terminate()
        worker_process.wait()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Render tự cấp phát biến môi trường PORT, app chính sẽ chạy ở cổng của Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
