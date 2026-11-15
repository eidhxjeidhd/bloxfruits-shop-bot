import os
import sqlite3
import uuid
from flask import Flask, redirect, render_template_string, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Thư mục lưu trữ file trên Render
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Khởi tạo Database SQLite
def init_db():
    conn = sqlite3.connect('cloud.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            filename TEXT,
            original_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mini Cloud Storage</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 750px; }
        .card { background: #1e293b; padding: 25px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #334155; margin-bottom: 20px; }
        h2 { color: #38bdf8; margin-top: 0; text-align: center; }
        .upload-box { border: 2px dashed #475569; padding: 20px; text-align: center; border-radius: 10px; background: #0f172a; margin-bottom: 15px; }
        input[type="file"] { color: #94a3b8; margin-bottom: 10px; }
        button { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; }
        button:hover { background: #0ea5e9; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: #38bdf8; }
        a { color: #38bdf8; text-decoration: none; word-break: break-all; }
        a:hover { text-decoration: underline; }
        .badge { background: #065f46; color: #34d399; padding: 6px 10px; border-radius: 8px; font-size: 12px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>☁️ Mini Cloud Storage</h2>
            <div class="badge">🌐 Đang chạy công khai trên Render</div>
            <form action="/upload" method="POST" enctype="multipart/form-data">
                <div class="upload-box">
                    <input type="file" name="file" required><br>
                    <span style="color: #64748b; font-size: 13px;">Chọn file bất kỳ để tải lên mây</span>
                </div>
                <button type="submit">🚀 Tải Lên Cloud</button>
            </form>
        </div>

        <div class="card">
            <h3 style="color: #e2e8f0; margin-top: 0;">📂 Danh Sách File Đã Tải Lên</h3>
            <table>
                <thead>
                    <tr>
                        <th>Tên File</th>
                        <th>Link Tải Công Khai</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in files %}
                    <tr>
                        <td><strong>{{ file[2] }}</strong></td>
                        <td><a href="{{ request.url_root }}d/{{ file[1] }}" target="_blank">{{ request.url_root }}d/{{ file[1] }}</a></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="2" style="text-align: center; color: #64748b;">Chưa có file nào được tải lên.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect('cloud.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT id, code, original_name FROM files ORDER BY id DESC')
    files = cursor.fetchall()
    conn.close()
    return render_template_string(DASHBOARD_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('home'))
    
    if file:
        original_name = secure_filename(file.filename)
        code = str(uuid.uuid4())[:8]
        saved_filename = f"{code}_{original_name}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(file_path)
        
        conn = sqlite3.connect('cloud.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO files (code, filename, original_name) VALUES (?, ?, ?)', 
                       (code, saved_filename, original_name))
        conn.commit()
        conn.close()
        
    return redirect(url_for('home'))

@app.route('/d/<code>')
def download_file(code):
    conn = sqlite3.connect('cloud.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT filename, original_name FROM files WHERE code = ?', (code,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        saved_filename, original_name = row
        return send_from_directory(app.config['UPLOAD_FOLDER'], saved_filename, as_attachment=True, download_name=original_name)
    else:
        return "<h2 style='text-align:center; color:#ef4444; margin-top:50px; font-family:sans-serif;'>❌ File không tồn tại!</h2>", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
