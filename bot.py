import os
import re
import logging
import instaloader
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ====== ТАНЗИМОТ ======
BOT_TOKEN = "8916625204:AAGrGy2kor7p96gIKKxZ29XcBq4cYtkBZ_0"
DOWNLOAD_DIR = "downloads"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
L = instaloader.Instaloader(
    dirname_pattern=DOWNLOAD_DIR,
    save_metadata=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    post_metadata_txt_pattern="",
)

INSTAGRAM_POST_RE = re.compile(
    r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! Ба ман линки пости Instagram (видео/сурат) фиристед, "
        "ё фармони /pfp username-ро барои гирифтани акси профил истифода баред.\n\n"
        "Мисол: /pfp instagram"
    )


async def download_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = INSTAGRAM_POST_RE.search(text)

    if not match:
        await update.message.reply_text(
            "Линки дуруст ёфт нашуд. Лутфан линки пости Instagram фиристед "
            "(масалан: https://www.instagram.com/p/XXXXXXXXX/)"
        )
        return

    shortcode = match.group(1)
    await update.message.reply_text("Дар ҳоли зеркашӣ... ⏳")

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=shortcode)

        folder = os.path.join(DOWNLOAD_DIR, shortcode)
        sent_any = False
        for fname in sorted(os.listdir(folder)):
            fpath = os.path.join(folder, fname)
            if fname.endswith((".mp4",)):
                await update.message.reply_video(video=open(fpath, "rb"))
                sent_any = True
            elif fname.endswith((".jpg", ".jpeg", ".png")):
                await update.message.reply_photo(photo=open(fpath, "rb"))
                sent_any = True

        if not sent_any:
            await update.message.reply_text("Файл ёфт нашуд.")

    except Exception as e:
        logger.error(f"Хатогӣ: {e}")
        await update.message.reply_text(
            "Хатогӣ рух дод. Мумкин аст пост хусусӣ (private) бошад ё линк нодуруст бошад."
        )


async def profile_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Лутфан номи корбарро нависед. Мисол: /pfp instagram"
        )
        return

    username = context.args[0].lstrip("@")
    await update.message.reply_text(f"Дар ҳоли гирифтани акси профили @{username}... ⏳")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        pic_url = profile.profile_pic_url
        await update.message.reply_photo(photo=pic_url, caption=f"Акси профили @{username}")
    except instaloader.exceptions.ProfileNotExistsException:
        await update.message.reply_text("Чунин корбар ёфт нашуд.")
    except Exception as e:
        logger.error(f"Хатогӣ: {e}")
        await update.message.reply_text("Хатогӣ рух дод. Лутфан дертар кӯшиш кунед.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pfp", profile_picture))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_post))

    print("Бот кор карда истодааст...")
    app.run_polling()


if __name__ == "__main__":
    main()