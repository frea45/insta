import os
import tempfile
import instaloader
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PROXY

app = Client("insta-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def download_post(url_or_username):
    with tempfile.TemporaryDirectory() as tempdir:
        loader = instaloader.Instaloader(dirname_pattern=tempdir, download_videos=True, download_video_thumbnails=False,
                                         download_comments=False, save_metadata=False, compress_json=False)
        if PROXY:
            loader.context._session.proxies = PROXY

        if url_or_username.startswith("http"):
            shortcode = url_or_username.split("/")[-2]
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target="insta")
        else:
            username = url_or_username.replace("@", "")
            profile = instaloader.Profile.from_username(loader.context, username)
            loader.download_profile(profile, profile_pic_only=False)

        files = []
        for root, _, filenames in os.walk(tempdir):
            for f in filenames:
                path = os.path.join(root, f)
                if f.endswith((".jpg", ".mp4")):
                    files.append(path)

        return files

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply("سلام! یوزرنیم یا لینک پست اینستاگرام رو بفرست تا دانلود کنم.")

@app.on_message(filters.private & filters.text & ~filters.command(["start"]))
async def handle_instagram(client, message: Message):
    text = message.text.strip()
    try:
        await message.reply("در حال دریافت اطلاعات... لطفاً صبر کنید.")
        files = download_post(text)
        if not files:
            await message.reply("فایلی یافت نشد.")
            return

        for file in files:
            await client.send_document(chat_id=LOG_CHANNEL, document=file, caption=f"درخواست از: {message.from_user.mention}")
            await message.reply_document(file)
            os.remove(file)

    except Exception as e:
        await message.reply(f"خطا در پردازش: {e}")

if __name__ == "__main__":
    app.run()
