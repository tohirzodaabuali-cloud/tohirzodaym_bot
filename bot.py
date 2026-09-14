import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! 👋\n\n"
        "Ман боти TOHIRZODAYM ҳастам 🤖\n"
        "Ба зудӣ хизматрасониҳои бештар фаъол мешаванд!"
    )

app = ApplicationBuilder().token(8881388960:AAEB8J-KezgAhSwuDGFJWqBFA9IhuVvPUJc).build()

app.add_handler(CommandHandler("start", start))

print("Bot started...")
app.run_polling()
