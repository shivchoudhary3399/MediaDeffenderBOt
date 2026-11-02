import os
import asyncio
# ===== PYTHON 3.14 BUG FIX - SABSE UPAR HONA CHAHIYE =====
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# =========================================================

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

API_ID = int(os.environ.get("API_ID", 34021459))
API_HASH = os.environ.get("API_HASH", "723416ae8c8e85f7346d0546ddbca61a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9181804196:AAEP18Vrl8IrTiHDZmxBWQf-MVQhDj7cTxo")
GLOBAL_OWNER_ID = int(os.environ.get("OWNER_ID", 8543138859))
BOT_USERNAME = "ShivMediaDefender_bot"

TIMERS = defaultdict(lambda: 60)
APPROVED_USERS = defaultdict(set)
SUPER_APPROVERS = defaultdict(set)
APPROVED_MSGS = set()

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running - SHIV DEFENDER")
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"Web server on {port}")
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

app = Client("shiv_defender", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def extract_user_id(client, message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.mention
    if len(message.text.split()) > 1:
        arg = message.text.split()[1].strip()
        if arg.isdigit():
            try:
                u = await client.get_users(int(arg))
                return int(arg), u.mention
            except:
                return int(arg), f"`{arg}`"
        if arg.startswith("@"):
            try:
                u = await client.get_users(arg)
                return u.id, u.mention
            except:
                return None, None
    return None, None

async def is_gc_owner_simple(client, chat_id, user_id):
    if user_id == GLOBAL_OWNER_ID:
        return True
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status == "creator"
    except:
        return False

async def is_super_or_owner(client, chat_id, user_id):
    if user_id == GLOBAL_OWNER_ID or user_id in SUPER_APPROVERS[chat_id] or await is_gc_owner_simple(client, chat_id, user_id):
        return True
    return False

async def set_commands():
    cmds = [
        BotCommand("start", "Start bot"),
        BotCommand("settimer", "Set timer"),
        BotCommand("approve", "Approve user"),
        BotCommand("unapprove", "Unapprove"),
        BotCommand("superapprove", "GC Owner super"),
        BotCommand("superunapprove", "Remove super"),
        BotCommand("settings", "Settings"),
        BotCommand("ping", "Ping"),
    ]
    try:
        await app.set_bot_commands(cmds)
    except:
        pass

@app.on_message(filters.group & ~filters.bot, group=0)
async def defender(client, message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    uid = message.from_user.id
    if await is_gc_owner_simple(client, chat_id, uid) or uid == GLOBAL_OWNER_ID or uid in APPROVED_USERS[chat_id] or uid in SUPER_APPROVERS[chat_id] or message.id in APPROVED_MSGS:
        return
    is_media = bool(message.photo or message.video or message.animation or message.sticker or message.document or message.voice or message.video_note)
    if not is_media:
        return
    await asyncio.sleep(TIMERS[chat_id])
    if uid in APPROVED_USERS[chat_id] or uid in SUPER_APPROVERS[chat_id] or await is_gc_owner_simple(client, chat_id, uid) or message.id in APPROVED_MSGS:
        return
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    caption = f"SHIV MEDIA DEFENDER\n\nHello {message.from_user.mention}\nStatus Protected"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add To Group", url=f"https://t.me/{BOT_USERNAME}?startgroup&admin=invite_users")],
        [InlineKeyboardButton("Help Panel", callback_data="help_panel")]
    ])
    await message.reply(caption, reply_markup=buttons)

@app.on_callback_query()
async def cb_handler(client, cq):
    if cq.data == "help_panel":
        txt = "HELP\n/settimer 60\n/approve\n/superapprove @user\n/settings"
        try:
            await cq.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_home")]]))
        except:
            await cq.answer()
    elif cq.data == "back_home":
        try:
            await cq.message.delete()
        except:
            pass
        await start_cmd(client, cq.message)

@app.on_message(filters.command(["settimer", "ping", "settings", "approvedlist"]))
async def other_cmds(client, message):
    text = message.text.lower()
    chat_id = message.chat.id
    if "settimer" in text:
        if not await is_super_or_owner(client, chat_id, message.from_user.id):
            return await message.reply("Only GC Owner / Super")
        try:
            sec = int(message.text.split()[1])
            TIMERS[chat_id] = sec
            await message.reply(f"Timer {sec}s Set")
        except:
            await message.reply("Use /settimer 60")
    elif "ping" in text:
        await message.reply(f"Alive {TIMERS[chat_id]}s")
    else:
        await message.reply(f"Status {TIMERS[chat_id]}s Approved {len(APPROVED_USERS[chat_id])} Super {len(SUPER_APPROVERS[chat_id])}")

@app.on_message(filters.command(["approve", "unapprove", "superapprove", "superunapprove"]))
async def approve_cmds(client, message):
    chat_id = message.chat.id
    text = message.text.lower()
    if "superapprove" in text and "superunapprove" not in text:
        if not await is_gc_owner_simple(client, chat_id, message.from_user.id):
            return await message.reply("Only GC Owner Creator Can Give Super")
        uid, mention = await extract_user_id(client, message)
        if not uid:
            return await message.reply("Use /superapprove @username")
        SUPER_APPROVERS[chat_id].add(uid)
        APPROVED_USERS[chat_id].add(uid)
        await message.reply(f"Super Approved {mention} {uid}")
    elif "superunapprove" in text:
        if not await is_gc_owner_simple(client, chat_id, message.from_user.id):
            return
        uid, mention = await extract_user_id(client, message)
        if uid:
            SUPER_APPROVERS[chat_id].discard(uid)
            await message.reply(f"Super Removed {mention}")
    elif "approve" in text and "unapprove" not in text and "super" not in text:
        if not await is_super_or_owner(client, chat_id, message.from_user.id):
            return await message.reply("Only GC Owner / Super")
        uid, mention = await extract_user_id(client, message)
        if not uid:
            return await message.reply("Reply to user or /approve @user")
        APPROVED_USERS[chat_id].add(uid)
        if message.reply_to_message:
            APPROVED_MSGS.add(message.reply_to_message.id)
        await message.reply(f"Lifetime Approved {mention} {uid}")
    elif "unapprove" in text:
        if not await is_super_or_owner(client, chat_id, message.from_user.id):
            return
        uid, mention = await extract_user_id(client, message)
        if uid:
            APPROVED_USERS[chat_id].discard(uid)
            await message.reply(f"Unapproved {mention}")

async def main():
    await app.start()
    await set_commands()
    print("Bot Running - Render Fixed Final")
    await asyncio.sleep(9999999)

if __name__ == "__main__":
    asyncio.run(main())
