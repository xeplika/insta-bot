# filepath: [test.py](http://_vscodecontentref_/1)
import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")  # Railway-də TOKEN environment dəyişəni kimi saxlanılır

LANGUAGES = {
    "az": {"name": "Azərbaycan 🇦🇿", "welcome": "Salam! Instagram linki göndərin, video və ya şəkil yükləyim.", "loading": "🔄 Yüklənir..."},
    "ru": {"name": "Русский 🇷🇺", "welcome": "Отправьте ссылку Instagram, я скачаю фото или видео.", "loading": "🔄 Загрузка..."},
    "en": {"name": "English 🇬🇧", "welcome": "Send Instagram link, I will download photo or video.", "loading": "🔄 Loading..."},
}

LOADING_GIF_URL = "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif"  # lupa gif

user_lang = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="lang_az"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("👤 Sahibim", url="https://t.me/agayeefv")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Dil seçin / Choose language / Выберите язык:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("lang_"):
        lang = query.data.split("_")[1]
        user_lang[query.from_user.id] = lang
        await query.edit_message_text(LANGUAGES[lang]["welcome"])

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "az")
    text = update.message.text.strip()
    if "instagram.com" not in text:
        await update.message.reply_text("Zəhmət olmasa Instagram linki göndərin.")
        return

    await update.message.reply_text(LANGUAGES[lang]["loading"])
    await update.message.reply_animation(animation=LOADING_GIF_URL, caption="🔍")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
    ydl_opts = {
        'outtmpl': 'insta.%(ext)s',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            file_path = ydl.prepare_filename(info)
        with open(file_path, "rb") as media:
            await update.message.reply_document(document=media, filename=os.path.basename(file_path))
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram))
    print("🤖 Bot işə düşdü...")
    app.run_polling()

if __name__ == "__main__":
    main()