import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = "8664286603:AAHqLdiV8Ecw_zHurZEifaObLlaVkqZVBss"
ADMIN_ID = 8976860826

ACCOUNT_STOCKS = {
    "pack_700": [("user_700_1", "pass_700_1")],
    "pack_1500": [("ohyflrs333", "080439123")],
    "pack_godhuman": [("user_god_1", "pass_god_1")],
    "pack_full": [("user_full_1", "pass_full_1")],
}

waiting_for_bill = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 MUA ACC BLOX FRUITS", callback_data="buy_menu")],
        [InlineKeyboardButton("📞 Liên hệ Zalo", url="https://zalo.me/0338976200")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "CHÀO MỪNG ĐẾN VỚI GÀ GAMING SHOP\n\nBấm nút bên dưới để chọn loại acc cần mua nhé!"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "buy_menu" or data == "back_home":
        keyboard = [
            [InlineKeyboardButton("Acc Lv 700 - 10.000d", callback_data="pack_700")],
            [InlineKeyboardButton("Acc Lv 1500 - 20.000d", callback_data="pack_1500")],
            [InlineKeyboardButton("Max Level + Godhuman - 49.000d", callback_data="pack_godhuman")],
            [InlineKeyboardButton("Max Lv + Godhuman + Song Kiem - 69.000d", callback_data="pack_full")],
            [InlineKeyboardButton("🔙 Quay lại", callback_data="back_home")]
        ]
        await query.edit_message_text(
            "CHỌN GÓI ACC BLOX FRUITS BẠN MUỐN MUA:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("pack_"):
        pack_names = {
            "pack_700": ("Acc Lv 700", "10.000d"),
            "pack_1500": ("Acc Lv 1500", "20.000d"),
            "pack_godhuman": ("Max Level + Godhuman", "49.000d"),
            "pack_full": ("Max Lv + Godhuman + Song Kiem", "69.000d"),
        }
        p_name, p_price = pack_names.get(data, ("Acc", "0d"))
        
        if not ACCOUNT_STOCKS.get(data):
            await query.edit_message_text(
                f"Gói '{p_name}' đã hết hàng!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Chọn lại", callback_data="buy_menu")]])
            )
            return

        context.user_data["buying_pack_key"] = data
        context.user_data["buying_pack"] = p_name
        context.user_data["buying_price"] = p_price
        waiting_for_bill[query.from_user.id] = True

        await query.edit_message_text(
            f"Bạn đã chọn: {p_name} - {p_price}\n\n"
            "CHUYỂN KHOẢN ZALOPAY:\n"
            "SĐT: 0338976200\n"
            "Nội dung: Mua nick + SĐT của bạn\n\n"
            "Gửi ảnh chụp bill vào đây để bot duyệt nhé!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Chọn lại", callback_data="buy_menu")]])
        )

    elif data.startswith("approve_") or data.startswith("reject_"):
        action, target_user_id = data.split("_")[0], int(data.split("_")[1])
        if action == "approve":
            pack_key = context.user_data.get("buying_pack_key", "pack_1500")
            acc_user, acc_pass = ACCOUNT_STOCKS[pack_key].pop(0) if ACCOUNT_STOCKS.get(pack_key) else ("Hết", "Hết")
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"GIAO DỊCH THÀNH CÔNG!\nTài khoản: {acc_user}\nMật khẩu: {acc_pass}"
            )
            await query.edit_message_caption(caption=query.message.caption + "\n\nĐÃ DUYỆT!", reply_markup=None)
        else:
            await context.bot.send_message(chat_id=target_user_id, text="Giao dịch bị từ chối!")
            await query.edit_message_caption(caption=query.message.caption + "\n\nĐÃ TỪ CHỐI!", reply_markup=None)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if waiting_for_bill.get(user_id):
        await update.message.reply_text("Đã nhận bill! Chờ Gà Gaming duyệt nhé.")
        admin_keyboard = [
            [InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_{user_id}")],
            [InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_{user_id}")]
        ]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"Khách {user_id} vừa gửi bill mua hàng!",
            reply_markup=InlineKeyboardMarkup(admin_keyboard)
        )
        waiting_for_bill[user_id] = False

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
evel + Godhuman - 49.000d": (
            "pack_godhuman",
            "Max Level + Godhuman",
            "49.000d",
        ),
        "Max Lv + Godhuman + Song Kiem - 69.000d": (
            "pack_full",
            "Max Lv + Godhuman + Song Kiem",
            "69.000d",
        ),
    }

    pack_key, p_name, p_price = pack_mapping[text]

    if not ACCOUNT_STOCKS.get(pack_key) or len(ACCOUNT_STOCKS[pack_key]) == 0:
      await update.message.reply_text(
          f"Rất tiếc! Gói '{p_name}' hiện tại đã HẾT HÀNG.\n"
          "Bạn vui lòng chọn gói khác nhé!"
      )
      return

    context.user_data["buying_pack_key"] = pack_key
    context.user_data["buying_pack"] = p_name
    context.user_data["buying_price"] = p_price
    waiting_for_bill[user_id] = True

    keyboard = [[KeyboardButton("🔙 Quay lại menu chính")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Bạn đã chọn: {p_name}\n"
        f"Giá tiền: {p_price}\n\n"
        "HUONG DAN THANH TOAN ZALOPAY:\n"
        "1. Chuyển khoản qua số: 0338976200 (Chủ ví: Gà Gaming)\n"
        "2. Nội dung CK: Mua nick + SĐT của bạn\n\n"
        "Sau khi chuyển khoản xong, bạn hãy GỬI ẢNH CHỤP BILL vào đây để bot gửi cho Gà Gaming xác nhận nhé!",
        reply_markup=reply_markup,
    )


async def handle_incoming_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.message.from_user
  user_id = user.id

  if waiting_for_bill.get(user_id):
    pack_name = context.user_data.get("buying_pack", "Không rõ gói")
    pack_price = context.user_data.get("buying_price", "0đ")

    await update.message.reply_text(
        "Đã nhận được ảnh bill của bạn! Bot đã chuyển cho Gà Gaming kiểm tra, bạn chờ một lát nhé!"
    )

    admin_caption = (
        f"CO KHACH GUI BILL MUA HANG!\n\n"
        f"Khách: {user.full_name} (@{user.username or 'Không có'})\n"
        f"ID Khách: {user_id}\n"
        f"Gói mua: {pack_name} ({pack_price})\n\n"
        f"Kiểm tra ví ZaloPay xem đã nhận được tiền chưa rồi bấm nút duyệt bên dưới!"
    )

    admin_keyboard = [
        [
            KeyboardButton(f"✅ DUYET_{user_id}"),
            KeyboardButton(f"❌ TUNCHOI_{user_id}"),
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=admin_caption,
        reply_markup=reply_markup,
    )
    waiting_for_bill[user_id] = False
  else:
    await update.message.reply_text(
        "Bạn vui lòng bấm chọn gói mua hàng trước khi gửi ảnh nhé!"
    )


async def admin_approval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text
  user_id = update.message.from_user.id

  if user_id != ADMIN_ID:
    return

  if text.startswith("✅ DUYET_"):
    target_user_id = int(text.split("_")[1])
    pack_key = context.user_data.get("buying_pack_key", "pack_1500")

    if ACCOUNT_STOCKS.get(pack_key) and len(ACCOUNT_STOCKS[pack_key]) > 0:
      acc_user, acc_pass = ACCOUNT_STOCKS[pack_key].pop(0)
    else:
      acc_user, acc_pass = ("Hết tài khoản trong kho!", "Liên hệ Admin gấp!")

    account_info = (
        "GIAO DICH THANH CONG!\n\n"
        "Cảm ơn bạn đã ủng hộ Gà Gaming Shop. Dưới đây là thông tin tài khoản Blox Fruits của bạn:\n"
        f"Tài khoản: {acc_user}\n"
        f"Mật khẩu: {acc_pass}\n\n"
        "Bạn nhớ đăng nhập đổi mật khẩu ngay lập tức nhé!"
    )
    await context.bot.send_message(chat_id=target_user_id, text=account_info)
    await update.message.reply_text(
        "Đã duyệt và gửi tài khoản cho khách thành công!"
    )

  elif text.startswith("❌ TUNCHOI_"):
    target_user_id = int(text.split("_")[1])
    await context.bot.send_message(
        chat_id=target_user_id,
        text="Giao dịch của bạn không thành công hoặc ảnh bill không hợp lệ. Vui lòng liên hệ Gà Gaming để được hỗ trợ!",
    )
    await update.message.reply_text("Đã từ chối giao dịch!")


def main():
  app = ApplicationBuilder().token(TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(MessageHandler(filters.PHOTO, handle_incoming_photo))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages)
  )
  app.add_handler(
      MessageHandler(
          filters.TEXT & filters.Regex("^(✅ DUYET_|❌ TUNCHOI_)"),
          admin_approval_handler,
      )
  )

  print("Bot Gà Gaming phiên bản phím bấm trực tiếp đang chạy...")
  app.run_polling()


if __name__ == "__main__":
  main()
 select_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  data = query.data
  pack_names = {
      "pack_700": ("Acc Lv 700", "10.000d"),
      "pack_1500": ("Acc Lv 1500", "20.000d"),
      "pack_godhuman": ("Max Level + Godhuman", "49.000d"),
      "pack_full": ("Max Lv + Godhuman + Song Kiem", "69.000d"),
  }

  if data in pack_names:
    p_name, p_price = pack_names[data]

    # Kiểm tra xem gói này còn hàng trong kho không
    if not ACCOUNT_STOCKS.get(data) or len(ACCOUNT_STOCKS[data]) == 0:
      await query.edit_message_text(
          f"Rất tiếc! Gói '{p_name}' hiện tại đã HẾT HÀNG.\n"
          "Bạn vui lòng chọn gói khác hoặc quay lại sau nhé!",
          reply_markup=InlineKeyboardMarkup(
              [[InlineKeyboardButton("Chọn gói khác", callback_data="buy_menu")]]
          ),
      )
      return

    context.user_data["buying_pack_key"] = data
    context.user_data["buying_pack"] = p_name
    context.user_data["buying_price"] = p_price

    waiting_for_bill[query.from_user.id] = True

    text = (
        f"Bạn đã chọn: {p_name}\n"
        f"Giá tiền: {p_price}\n\n"
        "HUONG DAN THANH TOAN ZALOPAY:\n"
        "1. Chuyển khoản qua số: 0338976200 (Chủ ví: Gà Gaming)\n"
        "2. Nội dung CK: Mua nick + SĐT của bạn\n\n"
        "Sau khi chuyển khoản xong, bạn hãy GỬI ẢNH CHỤP BILL vào đây để bot gửi cho Gà Gaming xác nhận nhé!"
    )
    keyboard = [[InlineKeyboardButton("Chọn lại gói", callback_data="buy_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_incoming_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.message.from_user
  user_id = user.id

  if waiting_for_bill.get(user_id):
    pack_name = context.user_data.get("buying_pack", "Không rõ gói")
    pack_price = context.user_data.get("buying_price", "0đ")

    await update.message.reply_text(
        "Đã nhận được ảnh bill của bạn! Bot đã chuyển cho Gà Gaming kiểm tra, bạn chờ một lát nhé!"
    )

    admin_caption = (
        f"CO KHACH GUI BILL MUA HANG!\n\n"
        f"Khách: {user.full_name} (@{user.username or 'Không có'})\n"
        f"ID Khách: {user_id}\n"
        f"Gói mua: {pack_name} ({pack_price})\n\n"
        f"Kiểm tra ví ZaloPay xem đã nhận được tiền chưa rồi bấm nút dưới để duyệt tài khoản!"
    )

    admin_keyboard = [
        [
            InlineKeyboardButton(
                "Xác nhận đúng tiền (Gửi Acc)",
                callback_data=f"approve_{user_id}",
            )
        ],
        [
            InlineKeyboardButton(
                "Sai tiền / Từ chối", callback_data=f"reject_{user_id}"
            )
        ],
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=admin_caption,
        reply_markup=InlineKeyboardMarkup(admin_keyboard),
    )

    waiting_for_bill[user_id] = False
  else:
    await update.message.reply_text(
        "Bạn vui lòng bấm chọn gói mua hàng trước khi gửi ảnh nhé!"
    )


async def admin_approval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  data = query.data
  parts = data.split("_")
  action = parts[0]
  target_user_id = int(parts[1])

  if action == "approve":
    pack_key = context.user_data.get("buying_pack_key", "pack_1500")

    if ACCOUNT_STOCKS.get(pack_key) and len(ACCOUNT_STOCKS[pack_key]) > 0:
      acc_user, acc_pass = ACCOUNT_STOCKS[pack_key].pop(0)
    else:
      acc_user, acc_pass = (
          "Hết tài khoản trong kho!",
          "Liên hệ Admin gấp!",
      )

    account_info = (
        "GIAO DICH THANH CONG!\n\n"
        "Cảm ơn bạn đã ủng hộ Gà Gaming Shop. Dưới đây là thông tin tài khoản Blox Fruits của bạn:\n"
        f"Tài khoản: {acc_user}\n"
        f"Mật khẩu: {acc_pass}\n\n"
        "Bạn nhớ đăng nhập đổi mật khẩu ngay lập tức nhé!"
    )
    await context.bot.send_message(chat_id=target_user_id, text=account_info)
    await query.edit_message_caption(
        caption=query.message.caption + "\n\nDA DUYET & GUI ACC CHO KHACH!",
        reply_markup=None,
    )

  elif action == "reject":
    await context.bot.send_message(
        chat_id=target_user_id,
        text="Giao dịch của bạn không thành công hoặc ảnh bill không hợp lệ. Vui lòng liên hệ Gà Gaming để được hỗ trợ!",
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\nDA TU CHOI GIAO DICH!",
        reply_markup=None,
    )


async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  data = query.data

  if data == "buy_menu" or data == "back_home":
    await buy_menu(update, context)
  elif data.startswith("pack_"):
    await select_package(update, context)
  elif data.startswith("approve_") or data.startswith("reject_"):
    await admin_approval_handler(update, context)


def main():
  app = ApplicationBuilder().token(TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_router))
  app.add_handler(MessageHandler(filters.PHOTO, handle_incoming_photo))

  print("Bot Gà Gaming đang chạy...")
  app.run_polling()


if __name__ == "__main__":
  main()
