import os
import tempfile
import instaloader
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

proxies = {
    "http": "http://138.2.86.126:80",
    "https": "http://138.2.86.126:80"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

app = Client("insta", api_id=int(os.environ.get("API_ID")), api_hash=os.environ.get("API_HASH"), bot_token=os.environ.get("BOT_TOKEN"))

LOG_CHANNEL = -1001792962793

@app.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply("سلام! یوزرنیم یا لینک اینستاگرام رو بفرست تا برات دانلود کنم.")

@app.on_message(filters.private & filters.text)
async def handle_instagram(client: Client, message: Message):
    text = message.text.strip()

    if text.startswith("@"):
        username = text[1:]
        try:
            url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
            resp = requests.get(url, headers=headers, proxies=proxies)
            data = resp.json()
            profile_pic_url = data["data"]["user"]["profile_pic_url_hd"]
            full_name = data["data"]["user"]["full_name"]
            bio = data["data"]["user"]["biography"]
            followers = data["data"]["user"]["edge_followed_by"]["count"]
            following = data["data"]["user"]["edge_follow"]["count"]

            caption = f"👤 {full_name}\n\n{bio}\n\n👥 دنبال‌کننده: {followers}\n▶️ دنبال‌شونده: {following}"

            downloaded = requests.get(profile_pic_url, proxies=proxies)
            photo_path = os.path.join(tempfile.gettempdir(), f"{username}.jpg")
            with open(photo_path, "wb") as f:
                f.write(downloaded.content)

            await client.send_photo(message.chat.id, photo=photo_path, caption=caption)
            await client.send_photo(LOG_CHANNEL, photo=photo_path, caption=f"Profile: @{username}")

            os.remove(photo_path)

        except Exception as e:
            await message.reply(f"خطا در دریافت اطلاعات پروفایل: {e}")

    elif "instagram.com" in text:
        try:
            loader = instaloader.Instaloader(
                dirname_pattern=tempfile.gettempdir(),
                download_videos=False,
                download_video_thumbnails=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False
            )

            post = instaloader.Post.from_shortcode(loader.context, text.split("/")[-2])
            loader.download_post(post, target="insta")

            file_path = None
            for file in os.listdir("insta"):
                if file.endswith(".jpg") or file.endswith(".mp4"):
                    file_path = os.path.join("insta", file)
                    break

            if file_path:
                if file_path.endswith(".jpg"):
                    await client.send_photo(message.chat.id, photo=file_path)
                    await client.send_photo(LOG_CHANNEL, photo=file_path)
                else:
                    await client.send_video(message.chat.id, video=file_path)
                    await client.send_video(LOG_CHANNEL, video=file_path)

            # پاکسازی
            for file in os.listdir("insta"):
                os.remove(os.path.join("insta", file))
            os.rmdir("insta")

        except Exception as e:
            await message.reply(f"خطا در دریافت پست: {e}")

    else:
        await message.reply("فرمت ورودی اشتباهه. یوزرنیم با @ یا لینک پست بفرست.")

if __name__ == "__main__":
    app.run()
