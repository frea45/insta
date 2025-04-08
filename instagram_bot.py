from pyrogram import Client, filters
from pyrogram.types import Message
from config import *

import instaloader
import os
import tempfile
import requests



app = Client("instagram_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

loader = instaloader.Instaloader(dirname_pattern=tempfile.gettempdir(), download_videos=False,
                                 download_video_thumbnails=False, download_comments=False,
                                 save_metadata=False, compress_json=False)

@app.on_message(filters.private & filters.text)
async def handle_message(client: Client, message: Message):
    text = message.text.strip()

    if text.startswith("@"):
        username = text[1:]
        try:
            profile = instaloader.Profile.from_username(loader.context, username)
            bio = profile.biography
            profile_pic_url = profile.profile_pic_url

            response = requests.get(profile_pic_url)
            if response.ok:
                sent = await client.send_photo(
                    chat_id=LOG_CHANNEL,
                    photo=response.content,
                    caption=f"پروفایل از @{username}\nbio:{bio}"
                )
                await sent.copy(chat_id=message.chat.id)
            else:
                await message.reply("دانلود عکس پروفایل انجام نشد.")
        except Exception as e:
            await message.reply(f"خطا در دریافت اطلاعات پروفایل: {e}")
    elif "instagram.com/reel/" in text:
        await handle_instagram_media(client, message, text)
    elif "instagram.com/p/" in text:
        await handle_instagram_media(client, message, text)
    else:
        await message.reply("فرمت ورودی نادرست است.")

async def handle_instagram_media(client, message, url):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = instaloader.Instaloader(dirname_pattern=tmpdir, download_video_thumbnails=False,
                                             save_metadata=False, download_comments=False)

            post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
            loader.download_post(post, target=post.owner_username)

            for file in os.listdir(tmpdir):
                if file.endswith((".jpg", ".mp4")):
                    file_path = os.path.join(tmpdir, file)
                    with open(file_path, "rb") as f:
                        if file.endswith(".jpg"):
                            sent = await client.send_photo(LOG_CHANNEL, f)
                        else:
                            sent = await client.send_video(LOG_CHANNEL, f)
                        await sent.copy(chat_id=message.chat.id)
    except Exception as e:
        await message.reply(f"خطا در دریافت پست: {e}")
