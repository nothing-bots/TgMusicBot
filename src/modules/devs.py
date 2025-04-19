#  Copyright (c) 2025 AshokShau
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the TgMusicBot project. All rights reserved where applicable.import subprocess
import asyncio
import subprocess
import inspect
import io
import os
import platform
import re
import socket
import sys
import traceback
import uuid
import signal
from html import escape
from sys import version as pyver
from typing import Any, Optional, Tuple

import psutil
from meval import meval
from ntgcalls import __version__ as ntgver
from pyrogram import __version__ as pyrover
from pytdbot import VERSION as pyTdVer
from pytdbot import Client, types

import config
from config import OWNER_ID, ALLOWED_USERS, UPSTREAM_REPO
from pytgcalls import __version__ as pytgver
from src.database import db
from src.logger import LOGGER
from src.modules.utils import Filter
from src.modules.utils.cacher import chat_cache
from src.modules.utils.play_helpers import del_msg, extract_argument


def format_exception(
    exp: BaseException, tb: Optional[list[traceback.FrameSummary]] = None
) -> str:
    """Formats an exception traceback as a string, similar to the Python interpreter."""

    if tb is None:
        tb = traceback.extract_tb(exp.__traceback__)

    # Replace absolute paths with relative paths
    cwd = os.getcwd()
    for frame in tb:
        if cwd in frame.filename:
            frame.filename = os.path.relpath(frame.filename)

    stack = "".join(traceback.format_list(tb))
    msg = str(exp)
    if msg:
        msg = f": {msg}"

    return f"Traceback (most recent call last):\n{stack}{type(exp).__name__}{msg}"


@Client.on_message(filters=Filter.command("eval"))
async def exec_eval(c: Client, m: types.Message):
    if int(m.from_id) not in OWNER_ID:
        return None

    text = m.text.split(None, 1)
    if len(text) <= 1:
        return await m.reply_text("Usage: /eval &lt code &gt")

    code = text[1]
    out_buf = io.StringIO()

    async def _eval() -> Tuple[str, Optional[str]]:
        async def send(*args: Any, **kwargs: Any) -> types.Message:
            return await m.reply_text(*args, **kwargs)

        def _print(*args: Any, **kwargs: Any) -> None:
            if "file" not in kwargs:
                kwargs["file"] = out_buf
                return print(*args, **kwargs)

        eval_vars = {
            "loop": c.loop,
            "client": c,
            "stdout": out_buf,
            "c": c,
            "m": m,
            "msg": m,
            "types": types,
            "send": send,
            "print": _print,
            "inspect": inspect,
            "os": os,
            "re": re,
            "sys": sys,
            "traceback": traceback,
            "uuid": uuid,
            "io": io,
            "chat_cache": chat_cache,
            "db": db,
        }

        try:
            return "", await meval(code, globals(), **eval_vars)
        except Exception as e:
            first_snip_idx = -1
            tb = traceback.extract_tb(e.__traceback__)
            for i, frame in enumerate(tb):
                if frame.filename == "<string>" or frame.filename.endswith("ast.py"):
                    first_snip_idx = i
                    break

            # Re-raise exception if it wasn't caused by the snippet
            if first_snip_idx == -1:
                raise e

            # Return formatted stripped traceback
            stripped_tb = tb[first_snip_idx:]
            formatted_tb = format_exception(e, tb=stripped_tb)
            return "⚠️ Error:\n\n", formatted_tb

    prefix, result = await _eval()

    if not out_buf.getvalue() or result is not None:
        print(result, file=out_buf)

    out = out_buf.getvalue()
    if out.endswith("\n"):
        out = out[:-1]

    result = f"""{prefix}<b>In:</b>
<pre language="python">{escape(code)}</pre>
<b>ᴏᴜᴛ:</b>
<pre language="python">{escape(out)}</pre>"""

    if len(result) > 4096:
        filename = f"/tmp/{uuid.uuid4().hex}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(out)

        caption = f"""{prefix}<b>ᴇᴠᴀʟ:</b>
    <pre language="python">{escape(code)}</pre>
    """
        await m.reply_document(
            document=types.InputFileLocal(filename),
            caption=caption,
            disable_notification=True,
            parse_mode="html",
        )
        return None

    await m.reply_text(str(result), parse_mode="html")


@Client.on_message(filters=Filter.command("stats"))
async def sys_stats(client: Client, message: types.Message):
    if int(message.from_id) not in ALLOWED_USERS:
        await del_msg(message)
        return None

    sysroot = await message.reply_text(
        f"ɢᴇᴛᴛɪɴɢ {client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs, ɪᴛ'ʟʟ ᴛᴀᴋᴇ ᴀ ᴡʜɪʟᴇ..."
    )

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(socket.gethostname())
    architecture = platform.machine()
    mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    sp = platform.system()
    ram = f"{str(round(psutil.virtual_memory().total / 1024.0 ** 3))} ɢʙ"
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)

    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}ɢʜᴢ"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}ᴍʜᴢ"
    except Exception as e:
        LOGGER.warning(f"Error getting CPU frequency: {e}")
        cpu_freq = "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ"

    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    used = hdd.used / (1024.0**3)
    free = hdd.free / (1024.0**3)
    platform_release = platform.release()
    platform_version = platform.version()
    chats = len(await db.get_all_chats())
    users = len(await db.get_all_users())

    await sysroot.edit_text(
        f"""
<b><u>{client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs</u></b>

<b>Chats:</b> {chats}
<b>Users:</b> {users}

<b>Python:</b> {pyver.split()[0]}
<b>Pyrogram:</b> {pyrover}
<b>Py-TgCalls:</b> {pytgver}
<b>NTGCalls:</b> {ntgver}
<b>PyTdBot:</b> {pyTdVer}


<b>IP:</b> {ip_address}
<b>MAC:</b> {mac_address}
<b>Hostname:</b> {hostname}
<b>Platform:</b> {sp}
<b>Architecture:</b> {architecture}
<b>Platform Release:</b> {platform_release}
<b>Platform Version:</b> {platform_version}

<b><u>Storage</u></b>
<b>Available:</b> {total:.2f} GiB
<b>Used:</b> {used:.2f} GiB
<b>Free:</b> {free:.2f} GiB

<b>RAM:</b> {ram}
<b>Physical Cores:</b> {p_core}
<b>Total Cores:</b> {t_core}
<b>CPU Frequency:</b> {cpu_freq}""",
    )


@Client.on_message(filters=Filter.command("ac"))
async def active_vc(_: Client, message: types.Message):
    if int(message.from_id) not in ALLOWED_USERS:
        await del_msg(message)
        return

    active_chats = chat_cache.get_active_chats()
    if not active_chats:
        await message.reply_text("No active voice chats.")
        return

    text = f"🎵 <b>Active Voice Chats</b> ({len(active_chats)}):\n\n"

    for chat_id in active_chats:
        queue_length = chat_cache.count(chat_id)
        if current_song := chat_cache.get_current_song(chat_id):
            song_info = f"🎶 <b>Now Playing:</b> <a href='{current_song.url}'>{current_song.name}</a> - {current_song.artist} ({current_song.duration}s)"
        else:
            song_info = "🔇 No song playing."

        text += (
            f"➤ <b>Chat ID:</b> <code>{chat_id}</code>\n"
            f"📌 <b>Queue Size:</b> {queue_length}\n"
            f"{song_info}\n\n"
        )

    if len(text) > 4096:
        text = f"🎵 <b>Active Voice Chats</b> ({len(active_chats)})"

    reply = await message.reply_text(text, disable_web_page_preview=True)
    if isinstance(reply, types.Error):
        return await message.reply_text(reply.message)


@Client.on_message(filters=Filter.command("logger"))
async def logger(c: Client, message: types.Message):
    if int(message.from_id) not in ALLOWED_USERS:
        await del_msg(message)
        return

    if config.LOGGER_ID == 0 or not config.LOGGER_ID:
        await message.reply_text("Please set LOGGER_ID in .env first.")
        return None

    args = extract_argument(message.text)
    enabled = await db.get_logger_status(c.me.id)
    if not args:
        await message.reply_text(
            "Usage: /logger [enable|disable|on|off]\n\nCurrent status: "
            + ("enabled" if enabled else "disabled")
        )
        return

    if args.lower() in ["on", "enable"]:
        await db.set_logger_status(c.me.id, True)
        await message.reply_text("Logger enabled.")
    elif args.lower() in ["off", "disable"]:
        await db.set_logger_status(c.me.id, False)
        await message.reply_text("Logger disabled.")
    else:
        await message.reply_text(
            f"Usage: /logger [enable|disable]\n\nYour argument is {args}"
        )




import asyncio
import os
import subprocess
import sys
from html import escape
import signal

from config import UPSTREAM_REPO, ALLOWED_USERS
from pytdbot import Client, types
from src.logger import LOGGER
from src.modules.utils import Filter


@Client.on_message(Filter.command("update"))
async def update_bot(c: Client, m: types.Message):
    if int(m.from_id) not in ALLOWED_USERS:
        await m.delete()
        return

    status_msg = await m.reply_text("🔄 Pulling latest updates from upstream...")

    try:
        # Pull the latest updates from the upstream repository
        pull_process = subprocess.run(
            ["git", "pull", UPSTREAM_REPO],
            capture_output=True, text=True
        )
        pull_output = pull_process.stdout + pull_process.stderr

        if "Already up to date." in pull_output:
            await status_msg.edit_text("✅ Bot is already up to date.")
            return

        # Install dependencies after pulling changes
        await status_msg.edit_text("📦 Installing updated dependencies...")

        if os.path.isfile("requirements.txt"):
            install_process = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True, text=True
            )
            install_output = install_process.stdout + install_process.stderr
            LOGGER.info("Dependencies installed:\n" + install_output)

        # Notify that the update is complete and restart the bot
        await status_msg.edit_text("✅ Update complete! Restarting bot...")

        # Start new session with bash script
        subprocess.Popen(["bash", "start"])

        # Kill current bot process
        os.kill(os.getpid(), signal.SIGTERM)

    except Exception as e:
        LOGGER.error(f"Update : {e}")
        await status_msg.edit_text(
            f"❌ Update failed:\n<pre>{escape(str(e))}</pre>",
            parse_mode="html"
        )

@Client.on_message(Filter.command("restart"))
async def restart_bot(c: Client, m: types.Message):
    if int(m.from_id) not in ALLOWED_USERS:
        await m.delete()
        return

    status_msg = await m.reply_text("🔄 Restarting bot...")

    try:
        # Start new session with bash script
        subprocess.Popen(["bash", "start"])

        # Kill current bot process to restart
        os.kill(os.getpid(), signal.SIGTERM)

    except Exception as e:
        LOGGER.error(f"Restart : {e}")
        await status_msg.edit_text(
            f"❌ Restart failed:\n<pre>{escape(str(e))}</pre>",
            parse_mode="html"
    )
