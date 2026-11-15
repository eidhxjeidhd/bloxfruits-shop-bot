import os
import sqlite3
import uuid
from flask import Flask, redirect, render_template_string, request, url_for
from pyngrok import ngrok, conf

app = Flask(__name__)

# Tự động nhận diện Authtoken từ biến môi trường khi chạy lệnh
auth_token = os.environ.get("NGROK_AUTHTOKEN")
if auth_token:
    conf.get_default().auth_token = auth_token

# Khởi tạo Database SQLite cục bộ trên Termux
def init_db():
    conn = sqlite3.connect('cloud.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

PUBLIC_URL = ""

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Termux Auto Cloud</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 500px; width: 90%; border: 1px solid #334155; }
        h2 { color: #38bdf8; margin-top: 0; text-align: center; }
        textarea { width: 100%; height: 100px; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 10px; border-radius: 8px; box-sizing: border-box; resize: vertical; font-size: 14px; }
        button { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 15px; font-size: 16px; }
        button:hover { background: #0ea5e9; }
        .result { margin-top: 20px; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; }
        a { color: #38bdf8; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .public-badge { background: #065f46; color: #34d399; padding: 6px 10px; border-radius: 8px; font-size: 12px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <h2>☁️ Termux Auto Cloud</h2>
        <div class="public-badge">🌐 Đang mở online qua Ngrok</div>
        <form action="/add" method="POST">
            <textarea name="content" placeholder="Nhập nội dung cần lưu trữ vào đây..." required></textarea>
            <button type="submit">Tạo Link Lưu Trữ</button>
        </form>
        {% if link %}
        <div class="result">
            <p style="margin:0 0 5px 0; color:#94a3b8; font-size:13px;">Đã tạo link thành công:</p>
            <a href="{{ link }}" target="_blank">{{ link }}</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

VIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xem Nội Dung - Cloud</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 600px; width: 90%; border: 1px solid #334155; word-break: break-word; }
        h2 { color: #38bdf8; margin-top: 0; }
        pre { white-space: pre-wrap; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; color: #e2e8f0; font-family: monospace; font-size: 14px; }
        .back { display: inline-block; margin-top: 15px; color: #38bdf8; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📄 Nội Dung Lưu Trữ</h2>
        <pre>{{ content }}</pre>
        <a class="back" href="/">← Quay lại trang chủ</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, link=None)

@app.route('/add', methods=['POST'])
def add_content():
    content = request.form.get('content')
    if not content:
        return redirect(url_for('home'))
        
    code = str(uuid.uuid4())[:6]
    
    conn = sqlite3.connect('cloud.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO links (code, content) VALUES (?, ?)', (code, content))
    conn.commit()
    conn.close()
    
    link = f"{PUBLIC_URL}/s/{code}"
    return render_template_string(HOME_TEMPLATE, link=link)

@app.route('/s/<code>')
def view_content(code):
    conn = sqlite3.connect('cloud.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM links WHERE code = ?', (code,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return render_template_string(VIEW_TEMPLATE, content=row[0])
    else:
        return "<h2 style='text-align:center; color:#ef4444; margin-top:50px; font-family:sans-serif;'>❌ Link không tồn tại hoặc đã bị xóa!</h2>", 404

if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    PUBLIC_URL = str(public_url).split('"')[1]
    
    print(f"\n==============================================")
    print(f"🌐 LINK TRANG CHỦ CÔNG KHAI: {PUBLIC_URL}")
    print(f"==============================================\n")
    
    app.run(host='0.0.0.0', port=5000)
