#  Copyright (c) 2025 AshokShau
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the TgMusicBot project. All rights reserved where applicable.
import time
from datetime import datetime
from types import NoneType

from cachetools import TTLCache
from pytdbot import Client, types

from src import __version__
from src.database import db
from src.modules.utils import Filter, sec_to_min
from src.modules.utils.admins import load_admin_cache
from src.modules.utils.buttons import add_me_button, SupportButtons
from src.modules.utils.cacher import chat_cache
from src.modules.utils.play_helpers import (
    chat_invite_cache,
    check_user_status,
    user_status_cache,
)
from src.pytgcalls import call

@Client.on_message(filters=Filter.command("start"))
async def start_cmd(c: Client, message: types.Message):
    me: types.User = await c.getMe()
    chat_id = message.chat_id
    if chat_id < 0:
        await db.add_chat(chat_id)
        await message.reply_text("‼️This command works in private chat only. Please message me in PM.")
        return
    else:
        await db.add_user(chat_id)

    text = f"""
<b>нєу {await message.mention(parse_mode='html')}, </b>🥀

๏ ᴛʜɪs ɪs {me.first_name} !

➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.

<b><u>Sᴜᴘᴘᴏʀᴛᴇᴅ Pʟᴀᴛғᴏʀᴍs</u></b> : ʏᴏᴜᴛᴜʙᴇ, sᴘᴏᴛɪғʏ, ʀᴇssᴏ, ᴀᴘᴘʟᴇ ᴍᴜsɪᴄ ᴀɴᴅ sᴏᴜɴᴅᴄʟᴏᴜᴅ.
──────────────────
<b>๏ ᴜsᴇ /help ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.</b>
    """
    bot_username = c.me.usernames.editable_username
    photo_url = "https://graph.org/file/f20072ed0125e05c4a179-749b57b82ab375adfb.jpg"  # replace this with your desired image URL

    reply = await message.reply_photo(
        photo=photo_url,
        caption=text,
        parse_mode="html",
        reply_markup=add_me_button(bot_username)
    )

    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending start message: {reply.message}")

    return None

@Client.on_message(filters=Filter.command("help"))
async def help_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id

    if chat_id < 0:
        await message.reply_text("❌ This command works in private chat only. Please message me in PM.")
        return

    text = f"""<b>Help for {c.me.first_name}:</b>

<b>/start:</b> Start the bot.
<b>/reload:</b> Reload chat administrator list.
<b>/authlist:</b> Get the list of authorized users.
<b>/play:</b> Reply to an audio or provide a song name to play music.
<b>/vplay:</b> Reply to a video or provide a song name to play video.
<b>/speed:</b> Change playback speed (0.5 - 4.0).
<b>/skip:</b> Skip the current song.
<b>/remove x:</b> Remove song from queue.
<b>/pause:</b> Pause the song.
<b>/resume:</b> Resume.
<b>/end:</b> End playback.
<b>/seek:</b> Seek to a specific time.
<b>/mute:</b> Mute.
<b>/unmute:</b> Unmute.
<b>/volume:</b> Adjust volume.
<b>/loop:</b> Loop track.
<b>/queue:</b> View queue.
<b>/clear:</b> Clear queue.
<b>/song:</b> Download from YouTube, Spotify.
<b>/setPlayType:</b> Change play type.
<b>/privacy:</b> Privacy policy.

<b>Chat Owner Commands:</b>
/auth, /unauth, /buttons, /thumb

<b>Bot Owner Commands:</b>
/stats, /logger, /broadcast, /activevc

────────────────────────────────────
<b>Note:</b> This bot works best in groups and needs admin permissions to function.
"""

    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending help message: {reply.message}")


@Client.on_message(filters=Filter.command("privacy"))
async def privacy_handler(c: Client, message: types.Message):
    bot_name = c.me.first_name
    text = f"""
    <u><b>Privacy Policy for {bot_name}:</b></u>

<b>1. Data Storage:</b>
- {bot_name} does not store any personal data on the user's device.
- We do not collect or store any data about your device or personal browsing activity.

<b>2. What We Collect:</b>
- We only collect your Telegram <b>user ID</b> and <b>chat ID</b> to provide the music streaming and interaction functionalities of the bot.
- No personal data such as your name, phone number, or location is collected.

<b>3. Data Usage:</b>
- The collected data (Telegram UserID, ChatID) is used strictly to provide the music streaming and interaction functionalities of the bot.
- We do not use this data for any marketing or commercial purposes.

<b>4. Data Sharing:</b>
- We do not share any of your personal or chat data with any third parties, organizations, or individuals.
- No sensitive data is sold, rented, or traded to any outside entities.

<b>5. Data Security:</b>
- We take reasonable security measures to protect the data we collect. This includes standard practices like encryption and safe storage.
- However, we cannot guarantee the absolute security of your data, as no online service is 100% secure.

<b>6. Cookies and Tracking:</b>
- {bot_name} does not use cookies or similar tracking technologies to collect personal information or track your behavior.

<b>7. Third-Party Services:</b>
- {bot_name} does not integrate with any third-party services that collect or process your personal information, aside from Telegram's own infrastructure.

<b>8. Your Rights:</b>
- You have the right to request the deletion of your data. Since we only store your Telegram ID and chat ID temporarily to function properly, these can be removed upon request.
- You may also revoke access to the bot at any time by removing or blocking it from your chats.

<b>9. Changes to the Privacy Policy:</b>
- We may update this privacy policy from time to time. Any changes will be communicated through updates within the bot.

<b>10. Contact Us:</b>
If you have any questions or concerns about our privacy policy, feel free to contact us at <a href="https://t.me/DeadlineTechSupport">Support Group</a>

──────────────────
<b>Note:</b> This privacy policy is in place to help you understand how your data is handled and to ensure that your experience with {bot_name} is safe and respectful.
    """

    reply = await message.reply_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending privacy policy message: {reply.message}")
    return


rate_limit_cache = TTLCache(maxsize=100, ttl=180)


@Client.on_message(filters=Filter.command("reload"))
async def reload_cmd(c: Client, message: types.Message):
    user_id = message.from_id
    chat_id = message.chat_id
    if chat_id > 0:
        return

    if user_id in rate_limit_cache:
        last_used_time = rate_limit_cache[user_id]
        time_remaining = 180 - (datetime.now() - last_used_time).total_seconds()
        reply = await message.reply_text(
            f"🚫 You can use this command again in ({sec_to_min(time_remaining)} Min."
        )
        if isinstance(reply, types.Error):
            c.logger.warning(f"Error sending message: {reply} for chat {chat_id}")
        return

    rate_limit_cache[user_id] = datetime.now()
    reply = await message.reply_text("🔄 Reloading...")
    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending message: {reply} for chat {chat_id}")
        return

    ub = await call.get_client(chat_id)
    if isinstance(ub, (types.Error, NoneType)):
        return await reply.edit_text(
            "❌ Something went wrong. Assistant not found for this chat."
        )

    chat_invite_cache.pop(chat_id, None)
    user_key = f"{chat_id}:{ub.me.id}"
    user_status_cache.pop(user_key, None)

    if not chat_cache.is_active(chat_id):
        chat_cache.clear_chat(chat_id)

    load_admins, _ = await load_admin_cache(c, chat_id, True)

    ub_stats = await check_user_status(c, chat_id, ub.me.id)
    if isinstance(ub_stats, types.Error):
        ub_stats = ub_stats.message

    loaded = "✅" if load_admins else "❌"
    text = (
        f"<b>Assistant Status:</b> {ub_stats}\n"
        f"<b>Admins Loaded:</b> {loaded}\n"
        f"<b>» Reloaded by:</b> {await message.mention()}"
    )

    reply = await reply.edit_text(text)
    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending message: {reply} for chat {chat_id}")
    return

@Client.on_message(filters=Filter.command("ping"))
async def ping_cmd(c: Client, message: types.Message):
    start_time = time.time()

    # Set your desired photo URL
    photo_url = "https://graph.org/file/c6d2c40f1642a83ed0879-6df83b8ce09aadcbfb.jpg"
    bot_username = c.me.usernames.editable_username
    
    # Send initial photo reply
    reply = await message.reply_photo(
        photo=photo_url,
        caption=f"🏓 Pong!",
        reply_markup=SupportButtons(bot_username)
    )

    end_time = time.time()

    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending message: {reply}")
    else:
        latency_ms = (end_time - start_time) * 1000
        await reply.edit_text(
            caption=f"🏓 Pong! {latency_ms:.2f}ms",
            parse_mode="html",
            reply_markup=SupportButtons(bot_username)
        )

    return

@Client.on_message(filters=Filter.command("Clone"))
async def song_cmd(c: Client, message: types.Message):
    reply = await message.reply_text("🎶 USE: @HarryXRobot")
    if isinstance(reply, types.Error):
        c.logger.warning(f"Error sending message: {reply}")

    return
