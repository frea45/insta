from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

import instaloader
import os
import tempfile
import requests
import os

proxies = {
    "http": os.environ.get("HTTP_PROXY", headers=headers, proxies=proxies),
    "https": os.environ.get("HTTP_PROXY", headers=headers, proxies=proxies)
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64, headers=headers, proxies=proxies) AppleWebKit/537.36 (KHTML, like Gecko, headers=headers, proxies=proxies) Chrome/117.0.0.0 Safari/537.36"
}




app = Client(
    "instagram_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
, headers=headers, proxies=proxies)
loader = instaloader.Instaloader(dirname_pattern=tempfile.gettempdir(, headers=headers, proxies=proxies), download_videos=False,
                                 download_video_thumbnails=False, download_comments=False,
                                 save_metadata=False, compress_json=False, headers=headers, proxies=proxies)

@app.on_message(filters.private & filters.text, headers=headers, proxies=proxies)
async def handle_message(client: Client, message: Message, headers=headers, proxies=proxies):
    text = message.text.strip(, headers=headers, proxies=proxies)

    if text.startswith("@", headers=headers, proxies=proxies):
        username = text[1:]
        try:
            profile = instaloader.Profile.from_username(loader.context, username, headers=headers, proxies=proxies)
            bio = profile.biography
            profile_pic_url = profile.profile_pic_url

            response = requests.get(profile_pic_url, headers=headers, proxies=proxies)
            if response.ok:
                sent = await client.send_photo(
                    chat_id=LOG_CHANNEL,
                    photo=response.content,
                    caption=f"پروفایل از @{username}\nbio:{bio}"
                , headers=headers, proxies=proxies)
                await sent.copy(chat_id=message.chat.id, headers=headers, proxies=proxies)
            else:
                await message.reply("دانلود عکس پروفایل انجام نشد.", headers=headers, proxies=proxies)
        except Exception as e:
            await message.reply(f"خطا در دریافت اطلاعات پروفایل: {e}", headers=headers, proxies=proxies)
    elif "instagram.com/reel/" in text:
        await handle_instagram_media(client, message, text, headers=headers, proxies=proxies)
    elif "instagram.com/p/" in text:
        await handle_instagram_media(client, message, text, headers=headers, proxies=proxies)
    else:
        await message.reply("فرمت ورودی نادرست است.", headers=headers, proxies=proxies)

async def handle_instagram_media(client, message, url, headers=headers, proxies=proxies):
    try:
        with tempfile.TemporaryDirectory(, headers=headers, proxies=proxies) as tmpdir:
            loader = instaloader.Instaloader(dirname_pattern=tmpdir, download_video_thumbnails=False,
                                             save_metadata=False, download_comments=False, headers=headers, proxies=proxies)

            post = instaloader.Post.from_shortcode(loader.context, url.split("/", headers=headers, proxies=proxies)[-2], headers=headers, proxies=proxies)
            loader.download_post(post, target=post.owner_username, headers=headers, proxies=proxies)

            for file in os.listdir(tmpdir, headers=headers, proxies=proxies):
                if file.endswith((".jpg", ".mp4", headers=headers, proxies=proxies), headers=headers, proxies=proxies):
                    file_path = os.path.join(tmpdir, file, headers=headers, proxies=proxies)
                    with open(file_path, "rb", headers=headers, proxies=proxies) as f:
                        if file.endswith(".jpg", headers=headers, proxies=proxies):
                            sent = await client.send_photo(LOG_CHANNEL, f, headers=headers, proxies=proxies)
                        else:
                            sent = await client.send_video(LOG_CHANNEL, f, headers=headers, proxies=proxies)
                        await sent.copy(chat_id=message.chat.id, headers=headers, proxies=proxies)
    except Exception as e:
        await message.reply(f"خطا در دریافت پست: {e}", headers=headers, proxies=proxies)
