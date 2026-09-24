import telebot
from telebot import types
import sqlite3
from datetime import datetime

# ==================== CẤU HÌNH ====================
# ⚠️ THAY TOKEN MỚI (sau khi revoke token cũ) VÀO ĐÂY
TOKEN = "8664286603:AAHqLdiV8Ecw_zHurZEifaObLlaVkqZVBss"  # ← TOKEN CŨ, ĐÃ LỘ, PHẢI ĐỔI

# ⚠️ THAY ADMIN_ID BẰNG CHAT ID THẬT CỦA BẠN
# Cách lấy: chat với @userinfobot trên Telegram, nó sẽ trả về ID (dạng số)
ADMIN_ID = 8664286603  # ← Kiểm tra lại xem có đúng ID của bạn không

bot = telebot.TeleBot(TOKEN)

# ==================== DATABASE ====================
conn = sqlite3.connect("shop.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    joined_at TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    description TEXT,
    price INTEGER,
    username TEXT,
    password TEXT,
    status TEXT DEFAULT 'available',
    sold_to INTEGER,
    sold_at TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    account_id INTEGER,
    price INTEGER,
    purchased_at TEXT
)
""")
conn.commit()

# ==================== HELPER ====================
def get_user(user_id, username=""):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
    if not user:
        cur.execute(
            "INSERT INTO users (user_id, username, joined_at) VALUES (?, ?, ?)",
            (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cur.fetchone()
    return user

def get_balance(user_id):
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else 0

def update_balance(user_id, amount):
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def format_price(p):
    return f"{p:,}đ".replace(",", ".")

# ==================== KEYBOARDS ====================
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🛒 Xem Acc", callback_data="shop"),
        types.InlineKeyboardButton("💰 Nạp Tiền", callback_data="deposit"),
        types.InlineKeyboardButton("👤 Tài Khoản", callback_data="profile"),
        types.InlineKeyboardButton("📜 Lịch Sử", callback_data="history"),
        types.InlineKeyboardButton("🆘 Hỗ Trợ", callback_data="support"),
    )
    return kb

def back_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Quay lại", callback_data="main_menu"))
    return kb

def categories_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔰 Acc Thường", callback_data="cat_thuong"),
        types.InlineKeyboardButton("🍎 Acc Có Trái", callback_data="cat_trai"),
        types.InlineKeyboardButton("👑 Acc VIP", callback_data="cat_vip"),
        types.InlineKeyboardButton("🌟 Acc Siêu VIP", callback_data="cat_svip"),
    )
    kb.add(types.InlineKeyboardButton("⬅️ Quay lại", callback_data="main_menu"))
    return kb

# ==================== START ====================
@bot.message_handler(commands=["start"])
def cmd_start(message):
    user = get_user(message.from_user.id, message.from_user.username or "")
    balance = get_balance(message.from_user.id)
    text = (
        f"⚔️ <b>SHOP ACC BLOX FRUIT</b> ⚔️\n\n"
        f"👋 Xin chào <b>{message.from_user.first_name}</b>!\n"
        f"💵 Số dư của bạn: <b>{format_price(balance)}</b>\n\n"
        f"👇 Chọn chức năng bên dưới:"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data == "main_menu")
def cb_main_menu(call):
    balance = get_balance(call.from_user.id)
    text = (
        f"⚔️ <b>SHOP ACC BLOX FRUIT</b> ⚔️\n\n"
        f"💵 Số dư: <b>{format_price(balance)}</b>\n\n"
        f"👇 Chọn chức năng:"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=main_menu())

# ==================== SHOP ====================
@bot.callback_query_handler(func=lambda c: c.data == "shop")
def cb_shop(call):
    text = "🛒 <b>DANH MỤC ACC</b>\n\nChọn loại acc bạn muốn xem:"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=categories_menu())

@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def cb_category(call):
    category = call.data.replace("cat_", "")
    cat_name = {
        "thuong": "Acc Thường", "trai": "Acc Có Trái",
        "vip": "Acc VIP", "svip": "Acc Siêu VIP"
    }.get(category, "Không rõ")

    cur.execute(
        "SELECT id, title, price FROM accounts WHERE category=? AND status='available' ORDER BY price ASC LIMIT 10",
        (category,)
    )
    rows = cur.fetchall()

    if not rows:
        bot.edit_message_text(
            f"😢 Danh mục <b>{cat_name}</b> hiện chưa có acc nào.\nVui lòng quay lại sau!",
            call.message.chat.id, call.message.message_id,
            parse_mode="HTML", reply_markup=back_menu()
        )
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    for acc_id, title, price in rows:
        kb.add(types.InlineKeyboardButton(f"{title} — {format_price(price)}", callback_data=f"view_{acc_id}"))
    kb.add(types.InlineKeyboardButton("⬅️ Quay lại", callback_data="shop"))

    bot.edit_message_text(f"🛒 <b>{cat_name.upper()}</b>\n\nChọn acc để xem chi tiết:",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("view_"))
def cb_view_acc(call):
    acc_id = int(call.data.replace("view_", ""))
    cur.execute("SELECT * FROM accounts WHERE id=?", (acc_id,))
    acc = cur.fetchone()

    if not acc or acc[7] != "available":
        bot.answer_callback_query(call.id, "❌ Acc này đã bán hoặc không tồn tại!", show_alert=True)
        return

    _, category, title, desc, price, _, _, _, _, _ = acc
    balance = get_balance(call.from_user.id)

    text = (
        f"📦 <b>{title}</b>\n\n"
        f"📝 Mô tả: {desc}\n"
        f"💰 Giá: <b>{format_price(price)}</b>\n"
        f"💵 Số dư: <b>{format_price(balance)}</b>\n\n"
        f"{'✅ Bạn đủ tiền để mua!' if balance >= price else '❌ Bạn không đủ tiền!'}"
    )

    kb = types.InlineKeyboardMarkup(row_width=1)
    if balance >= price:
        kb.add(types.InlineKeyboardButton("🛒 MUA NGAY", callback_data=f"buy_{acc_id}"))
    else:
        kb.add(types.InlineKeyboardButton("💰 NẠP TIỀN", callback_data="deposit"))
    kb.add(types.InlineKeyboardButton("⬅️ Quay lại", callback_data=f"cat_{category}"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def cb_buy(call):
    acc_id = int(call.data.replace("buy_", ""))
    user_id = call.from_user.id

    cur.execute("SELECT * FROM accounts WHERE id=?", (acc_id,))
    acc = cur.fetchone()

    if not acc or acc[7] != "available":
        bot.answer_callback_query(call.id, "❌ Acc đã bị mua!", show_alert=True)
        return

    price = acc[4]
    balance = get_balance(user_id)

    if balance < price:
        bot.answer_callback_query(call.id, "❌ Bạn không đủ tiền!", show_alert=True)
        return

    update_balance(user_id, -price)
    cur.execute("UPDATE users SET total_spent = total_spent + ? WHERE user_id=?", (price, user_id))
    cur.execute("UPDATE accounts SET status='sold', sold_to=?, sold_at=? WHERE id=?",
                (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), acc_id))
    cur.execute("INSERT INTO purchases (user_id, account_id, price, purchased_at) VALUES (?, ?, ?, ?)",
                (user_id, acc_id, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    info = (
        f"✅ <b>MUA THÀNH CÔNG!</b>\n\n"
        f"📦 Acc: <b>{acc[2]}</b>\n"
        f"💰 Giá: <b>{format_price(price)}</b>\n\n"
        f"🔑 <b>THÔNG TIN ĐĂNG NHẬP:</b>\n"
        f"👤 Username: <code>{acc[5]}</code>\n"
        f"🔒 Password: <code>{acc[6]}</code>\n\n"
        f"⚠️ Vui lòng đổi mật khẩu ngay sau khi đăng nhập!\n"
        f"Cảm ơn bạn đã mua hàng ❤️"
    )
    bot.send_message(call.message.chat.id, info, parse_mode="HTML")

    bot.send_message(
        ADMIN_ID,
        f"🔔 <b>ĐƠN HÀNG MỚI</b>\n\n"
        f"👤 Khách: {call.from_user.first_name} (@{call.from_user.username})\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📦 Acc: {acc[2]}\n"
        f"💰 Giá: {format_price(price)}",
        parse_mode="HTML"
    )

    balance = get_balance(user_id)
    bot.edit_message_text(f"✅ Mua thành công! Số dư còn: <b>{format_price(balance)}</b>",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=back_menu())

# ==================== NẠP TIỀN ====================
@bot.callback_query_handler(func=lambda c: c.data == "deposit")
def cb_deposit(call):
    text = (
        "💰 <b>NẠP TIỀN</b>\n\n"
        "Chọn mệnh giá bạn muốn nạp:\n\n"
        "📌 Sau khi chuyển khoản, admin sẽ duyệt và cộng tiền cho bạn."
    )
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("20.000đ", callback_data="dep_20000"),
        types.InlineKeyboardButton("50.000đ", callback_data="dep_50000"),
        types.InlineKeyboardButton("100.000đ", callback_data="dep_100000"),
        types.InlineKeyboardButton("200.000đ", callback_data="dep_200000"),
        types.InlineKeyboardButton("500.000đ", callback_data="dep_500000"),
    )
    kb.add(types.InlineKeyboardButton("⬅️ Quay lại", callback_data="main_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dep_"))
def cb_deposit_amount(call):
    amount = int(call.data.replace("dep_", ""))
    user_id = call.from_user.id

    cur.execute(
        "INSERT INTO deposits (user_id, amount, method, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (user_id, amount, "bank", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    dep_id = cur.lastrowid

    text = (
        f"💰 <b>ĐƠN NẠP #{dep_id}</b>\n\n"
        f"💵 Số tiền: <b>{format_price(amount)}</b>\n\n"
        f"📌 <b>HƯỚNG DẪN:</b>\n"
        f"1. Chuyển khoản đến STK: <code>123456789</code>\n"
        f"2. Ngân hàng: <b>Vietcombank</b>\n"
        f"3. Nội dung CK: <code>NAP{dep_id}</code>\n\n"
        f"⚠️ Sau khi chuyển, nhấn nút bên dưới để báo admin."
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("✅ Tôi đã chuyển khoản", callback_data=f"confirm_dep_{dep_id}"))
    kb.add(types.InlineKeyboardButton("⬅️ Quay lại", callback_data="deposit"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_dep_"))
def cb_confirm_deposit(call):
    dep_id = int(call.data.replace("confirm_dep_", ""))
    bot.send_message(
        ADMIN_ID,
        f"🔔 <b>XÁC NHẬN NẠP TIỀN</b>\n\n"
        f"🆔 Đơn: #{dep_id}\n"
        f"👤 Khách: {call.from_user.first_name} (@{call.from_user.username})\n"
        f"🆔 User ID: <code>{call.from_user.id}</code>\n\n"
        f"Dùng lệnh <code>/duyet {dep_id}</code> để duyệt.",
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id, "✅ Đã báo admin! Vui lòng chờ duyệt.", show_alert=True)

# ==================== TÀI KHOẢN ====================
@bot.callback_query_handler(func=lambda c: c.data == "profile")
def cb_profile(call):
    user = get_user(call.from_user.id)
    balance, spent, joined = user[2], user[3], user[4]

    cur.execute("SELECT COUNT(*) FROM purchases WHERE user_id=?", (call.from_user.id,))
    total_acc = cur.fetchone()[0]

    text = (
        f"👤 <b>THÔNG TIN TÀI KHOẢN</b>\n\n"
        f"🆔 User ID: <code>{call.from_user.id}</code>\n"
        f"📛 Tên: {call.from_user.first_name}\n"
        f"💵 Số dư: <b>{format_price(balance)}</b>\n"
        f"💸 Đã chi: <b>{format_price(spent)}</b>\n"
        f"📦 Đã mua: <b>{total_acc} acc</b>\n"
        f"📅 Tham gia: {joined}"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=back_menu())

# ==================== LỊCH SỬ ====================
@bot.callback_query_handler(func=lambda c: c.data == "history")
def cb_history(call):
    cur.execute("""
        SELECT p.id, a.title, p.price, p.purchased_at
        FROM purchases p JOIN accounts a ON p.account_id = a.id
        WHERE p.user_id=? ORDER BY p.id DESC LIMIT 10
    """, (call.from_user.id,))
    rows = cur.fetchall()

    if not rows:
        text = "📜 Bạn chưa mua acc nào."
    else:
        text = "📜 <b>LỊCH SỬ MUA HÀNG</b>\n\n"
        for pid, title, price, time in rows:
            text += f"#{pid} — {title}\n💰 {format_price(price)} | 🕒 {time}\n\n"

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=back_menu())

# ==================== HỖ TRỢ ====================
@bot.callback_query_handler(func=lambda c: c.data == "support")
def cb_support(call):
    text = (
        "🆘 <b>HỖ TRỢ</b>\n\n"
        "Nếu gặp vấn đề, liên hệ admin:\n"
        f"👤 Admin: @your_username\n\n"
        "⏰ Thời gian hỗ trợ: 8h - 22h hàng ngày"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML", reply_markup=back_menu())

# ==================== ADMIN COMMANDS ====================
@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")
        return

    cur.execute("SELECT COUNT(*), SUM(price) FROM purchases")
    total_sold, total_revenue = cur.fetchone()
    total_revenue = total_revenue or 0

    cur.execute("SELECT COUNT(*) FROM accounts WHERE status='available'")
    available = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM deposits WHERE status='pending'")
    pending = cur.fetchone()[0]

    text = (
        f"👑 <b>ADMIN PANEL</b>\n\n"
        f"📦 Acc đã bán: <b>{total_sold}</b>\n"
        f"💰 Doanh thu: <b>{format_price(total_revenue)}</b>\n"
        f"🛒 Acc còn: <b>{available}</b>\n"
        f"⏳ Đơn nạp chờ: <b>{pending}</b>\n\n"
        f"<b>LỆNH:</b>\n"
        f"/themacc — Thêm acc mới\n"
        f"/xoaacc &lt;id&gt; — Xóa acc\n"
        f"/duyet &lt;id&gt; — Duyệt nạp tiền\n"
        f"/dsnap — Danh sách đơn nạp chờ"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=["themacc"])
def cmd_add_acc(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.reply_to(
        message,
        "📝 Nhập thông tin acc theo format:\n\n"
        "<code>category|title|description|price|username|password</code>\n\n"
        "Ví dụ:\n"
        "<code>vip|Acc VIP Trái Rồng|Level 1500, có trái Rồng|50000|user1|pass1</code>",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, process_add_acc)

def process_add_acc(message):
    try:
        parts = message.text.split("|")
        if len(parts) != 6:
            bot.reply_to(message, "❌ Sai format! Cần 6 phần.")
            return
        cat, title, desc, price, username, password = [p.strip() for p in parts]
        cur.execute(
            "INSERT INTO accounts (category, title, description, price, username, password, status) VALUES (?, ?, ?, ?, ?, ?, 'available')",
            (cat, title, desc, int(price), username, password)
        )
        conn.commit()
        bot.reply_to(message, f"✅ Đã thêm acc #{cur.lastrowid}: {title}")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")

@bot.message_handler(commands=["duyet"])
def cmd_approve(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        dep_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "❌ Dùng: /duyet <id>")
        return

    cur.execute("SELECT user_id, amount, status FROM deposits WHERE id=?", (dep_id,))
    row = cur.fetchone()
    if not row:
        bot.reply_to(message, "❌ Không tìm thấy đơn.")
        return
    if row[2] == "approved":
        bot.reply_to(message, "⚠️ Đơn này đã duyệt rồi.")
        return

    user_id, amount, _ = row
    update_balance(user_id, amount)
    cur.execute("UPDATE deposits SET status='approved' WHERE id=?", (dep_id,))
    conn.commit()

    bot.reply_to(message, f"✅ Đã duyệt đơn #{dep_id}, cộng {format_price(amount)} cho user {user_id}.")
    try:
        bot.send_message(user_id, f"✅ Đơn nạp #{dep_id} đã được duyệt!\n💰 +{format_price(amount)}")
    except:
        pass

@bot.message_handler(commands=["dsnap"])
def cmd_list_deposits(message):
    if message.from_user.id != ADMIN_ID:
        return
    cur.execute("SELECT id, user_id, amount, created_at FROM deposits WHERE status='pending' ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    if not rows:
        bot.reply_to(message, "✅ Không có đơn nạp nào chờ duyệt.")
        return
    text = "⏳ <b>ĐƠN NẠP CHỜ DUYỆT</b>\n\n"
    for did, uid, amount, t in rows:
        text += f"#{did} — User <code>{uid}</code> — {format_price(amount)} — {t}\n"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=["xoaacc"])
def cmd_del_acc(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        acc_id = int(message.text.split()[1])
        cur.execute("DELETE FROM accounts WHERE id=?", (acc_id,))
        conn.commit()
        bot.reply_to(message, f"✅ Đã xóa acc #{acc_id}.")
    except:
        bot.reply_to(message, "❌ Dùng: /xoaacc <id>")

# ==================== CHẠY BOT ====================
print("🤖 Bot đang chạy...")
print(f"👑 Admin ID: {ADMIN_ID}")
bot.infinity_polling()
