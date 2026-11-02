import os
import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from pyrogram import idle

# ===== YOUR CONFIG - RENDER ENV SE BHI LE SAKTA HAI =====
API_ID = int(os.environ.get("API_ID", 34021459))
API_HASH = os.environ.get("API_HASH", "723416ae8c8e85f7346d0546ddbca61a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9181804196:AAEP18Vrl8IrTiHDZmxBWQf-MVQhDj7cTxo")
GLOBAL_OWNER_ID = int(os.environ.get("OWNER_ID", 8543138859))
BOT_USERNAME = "ShivMediaDefender_bot"

TIMERS = defaultdict(lambda: 60)
APPROVED_USERS = defaultdict(set)
SUPER_APPROVERS = defaultdict(set)
APPROVED_MSGS = set()

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
    if user_id == GLOBAL_OWNER_ID:
        return True
    if user_id in SUPER_APPROVERS[chat_id]:
        return True
    if await is_gc_owner_simple(client, chat_id, user_id):
        return True
    return False

async def set_commands():
    cmds = [
        BotCommand("start", "✨ Start with premium panel"),
        BotCommand("settimer", "⏰ Set delete timer"),
        BotCommand("approve", "💎 Approve lifetime"),
        BotCommand("unapprove", "❌ Unapprove"),
        BotCommand("superapprove", "👑 GC Owner super power"),
        BotCommand("superunapprove", "👑 Remove super"),
        BotCommand("settings", "🛡️ GC settings"),
        BotCommand("approvedlist", "📜 Approved list"),
        BotCommand("ping", "🟢 Ping check"),
    ]
    try:
        await app.set_bot_commands(cmds)
        print("✅ Premium Commands Set")
    except Exception as e:
        print(f"Cmd Error {e}")

@app.on_message(filters.group & ~filters.bot, group=0)
async def defender(client, message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    uid = message.from_user.id
    if await is_gc_owner_simple(client, chat_id, uid):
        return
    if uid == GLOBAL_OWNER_ID:
        return
    if uid in APPROVED_USERS[chat_id] or uid in SUPER_APPROVERS[chat_id] or message.id in APPROVED_MSGS:
        return
    is_media = bool(message.photo or message.video or message.animation or message.sticker or message.document or message.voice or message.video_note)
    if not is_media:
        return
    await asyncio.sleep(TIMERS[chat_id])
    if uid in APPROVED_USERS[chat_id] or uid in SUPER_APPROVERS[chat_id]:
        return
    if await is_gc_owner_simple(client, chat_id, uid):
        return
    if message.id in APPROVED_MSGS:
        return
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    if message.chat.type.value == "private":
        caption = f"""
<blockquote>╭─── <emoji id=5373189671913735062>❄️</emoji> <b>ꜱʜɪᴠ • ᴍᴇᴅɪᴀ ᴅᴇꜰᴇɴᴅᴇʀ</b> <emoji id=5373189671913735062>❄️</emoji> ────╮
╰──────────────────────────╯

   <emoji id=5372981702439583899>💎</emoji> <b>ʜᴇʟʟᴏ</b> › {message.from_user.mention}
   <emoji id=5369897110776111316>⚡</emoji> <b>ꜱᴛᴀᴛᴜꜱ</b> › <emoji id=5373146461061551826>🟢</emoji> <i>ᴘʀᴏᴛᴇᴄᴛᴇᴅ</i>
   <emoji id=5373049855119827669>👑</emoji> <b>ꜱʏꜱᴛᴇᴍ</b> › <emoji id=5373215232639836487>🛡️</emoji> <i>GC Owner Based</i>
   <emoji id=5373032997818684207>🔥</emoji> <b>ᴍᴏᴅᴇ</b> › <emoji id=5373134151511221731>⚔️</emoji> <i>Premium</i>

────────────────────────────
  <emoji id=5373215232639836487>🛡️</emoji> <b>GC Owner = Full Control</b>
  <emoji id=5373134151511221731>⚔️</emoji> <b>Auto Delete After Timer</b>
  <emoji id=5373032997818684207>🔥</emoji> <b>Super Approve System</b>
────────────────────────────
</blockquote>
"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add To Group 💎", url=f"https://t.me/{BOT_USERNAME}?startgroup&admin=invite_users")],
            [InlineKeyboardButton("🆘 Help Panel ⚡", callback_data="help_panel")]
        ])
        await message.reply(caption, reply_markup=buttons)
    else:
        await message.reply(f"<blockquote><emoji id=5373215232639836487>🛡️</emoji> <b>Active</b> <emoji id=5372981702439583899>⏰</emoji> {TIMERS[message.chat.id]}s <emoji id=5373146461061551826>🟢</emoji></blockquote>")

@app.on_callback_query(filters.regex("help_panel"))
async def help_panel(client, cq):
    txt = f"""
<blockquote>╭─── <emoji id=5369897110776111316>⚡</emoji> <b>ꜱʜɪᴠ ʜᴇʟᴘ ᴘᴀɴᴇʟ</b> <emoji id=5369897110776111316>⚡</emoji> ────╮

<emoji id=5372981702439583899>💎</emoji> <b>/settimer</b> <emoji id=5372981702439583899>⏰</emoji>
   <emoji id=5373215232639836487>├</emoji> <emoji id=5369897110776111316>⚡</emoji> Use › Set auto delete delay
   <emoji id=5373215232639836487>└</emoji> <emoji id=5373035390491894327>👉</emoji> Ex › <code>/settimer 60</code>

<emoji id=5373215232639836487>🛡️</emoji> <b>/approve</b> <emoji id=5373215232639836487>🛡️</emoji>
   <emoji id=5373215232639836487>├</emoji> <emoji id=5369897110776111316>⚡</emoji> Use › Approve - never delete <emoji id=5373146461061551826>🟢</emoji>
   <emoji id=5373215232639836487>├</emoji> <emoji id=5373049855119827669>👑</emoji> Who › GC Owner / Super Only
   <emoji id=5373215232639836487>└</emoji> <emoji id=5373035390491894327>👉</emoji> Ex › Reply + <code>/approve</code>

<emoji id=5373049855119827669>👑</emoji> <b>/superapprove</b> <emoji id=5373049855119827669>👑</emoji> - GC Owner Only
   <emoji id=5373215232639836487>└</emoji> <emoji id=5373035390491894327>👉</emoji> Ex › <code>/superapprove @user</code>

<emoji id=5373134151511221731>📜</emoji> <b>/settings</b> - View status <emoji id=5372981702439583899>💎</emoji>
────────────────────────────
<emoji id=5373146461061551826>💎</emoji> GC Owner = Full Control <emoji id=5373146461061551826>🟢</emoji>
</blockquote>
"""
    try:
        await cq.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add To Group 💎", url=f"https://t.me/{BOT_USERNAME}?startgroup&admin=invite_users")],
            [InlineKeyboardButton("⬅️ Back 🔙", callback_data="back_home")]
        ]))
    except:
        await cq.answer()

@app.on_callback_query(filters.regex("back_home"))
async def back_home(client, cq):
    try:
        await cq.message.delete()
    except:
        pass
    await start_cmd(client, cq.message)

@app.on_message(filters.command(["settimer", f"settimer@{BOT_USERNAME}"]) & filters.group)
async def set_timer(client, message):
    if not await is_super_or_owner(client, message.chat.id, message.from_user.id):
        return await message.reply("<blockquote><emoji id=5373049855119827669>❌</emoji> <b>Only GC Owner / Super</b> <emoji id=5373215232639836487>🛡️</emoji></blockquote>")
    try:
        sec = int(message.text.split()[1])
        TIMERS[message.chat.id] = sec
        await message.reply(f"<blockquote><emoji id=5373146461061551826>✅</emoji> <emoji id=5372981702439583899>⏰</emoji> <b>Timer {sec}s Set</b> <emoji id=5373146461061551826>🟢</emoji></blockquote>")
    except:
        await message.reply("<blockquote>Use: <code>/settimer 60</code></blockquote>")

@app.on_message(filters.command(["approve", f"approve@{BOT_USERNAME}"]) & filters.group)
async def approve_cmd(client, message):
    if not await is_super_or_owner(client, message.chat.id, message.from_user.id):
        return await message.reply("<blockquote><emoji id=5373049855119827669>❌</emoji> <b>Only GC Owner / Super Can Approve</b> <emoji id=5373215232639836487>🛡️</emoji></blockquote>")
    uid, mention = await extract_user_id(client, message)
    if not uid:
        return await message.reply("<blockquote><emoji id=5372981702439583899>❌</emoji> Reply or give ID/Username</blockquote>")
    APPROVED_USERS[message.chat.id].add(uid)
    if message.reply_to_message:
        APPROVED_MSGS.add(message.reply_to_message.id)
    await message.reply(f"<blockquote><emoji id=5373146461061551826>✅</emoji> <emoji id=5372981702439583899>💎</emoji> <b>Lifetime Approved</b> › {mention} <code>{uid}</code> <emoji id=5373146461061551826>🟢</emoji></blockquote>")

@app.on_message(filters.command(["unapprove", f"unapprove@{BOT_USERNAME}"]) & filters.group)
async def unapprove_cmd(client, message):
    if not await is_super_or_owner(client, message.chat.id, message.from_user.id):
        return
    uid, mention = await extract_user_id(client, message)
    if not uid:
        return
    APPROVED_USERS[message.chat.id].discard(uid)
    await message.reply(f"<blockquote><emoji id=5373215232639836487>🛡️</emoji> <b>Unapproved</b> › {mention}</blockquote>")

@app.on_message(filters.command(["superapprove", f"superapprove@{BOT_USERNAME}"]) & filters.group)
async def superapprove_cmd(client, message):
    if not await is_gc_owner_simple(client, message.chat.id, message.from_user.id):
        return await message.reply(f"<blockquote><emoji id=5373049855119827669>❌</emoji> <b>Only GC Owner (Creator) Can Give Super</b> <emoji id=5373215232639836487>🛡️</emoji></blockquote>")
    uid, mention = await extract_user_id(client, message)
    if not uid:
        return await message.reply("<blockquote>Use: <code>/superapprove @username</code></blockquote>")
    SUPER_APPROVERS[message.chat.id].add(uid)
    APPROVED_USERS[message.chat.id].add(uid)
    await message.reply(f"<blockquote><emoji id=5373049855119827669>👑</emoji> <b>Super Approved</b> › {mention} <code>{uid}</code> <emoji id=5373032997818684207>🔥</emoji></blockquote>")

@app.on_message(filters.command(["superunapprove", f"superunapprove@{BOT_USERNAME}"]) & filters.group)
async def superunapprove_cmd(client, message):
    if not await is_gc_owner_simple(client, message.chat.id, message.from_user.id):
        return
    uid, mention = await extract_user_id(client, message)
    if not uid:
        return
    SUPER_APPROVERS[message.chat.id].discard(uid)
    await message.reply(f"<blockquote><emoji id=5373049855119827669>👑</emoji> <b>Super Removed</b> › {mention}</blockquote>")

@app.on_message(filters.command(["settings", "approvedlist", f"settings@{BOT_USERNAME}", f"approvedlist@{BOT_USERNAME}"]) & filters.group)
async def settings_cmd(client, message):
    await message.reply(f"<blockquote><emoji id=5373215232639836487>🛡️</emoji> <b>Status</b> <emoji id=5372981702439583899>⏰</emoji> {TIMERS[message.chat.id]}s | <emoji id=5372981702439583899>💎</emoji> Approved {len(APPROVED_USERS[message.chat.id])} | <emoji id=5373049855119827669>👑</emoji> Super {len(SUPER_APPROVERS[message.chat.id])}</blockquote>")

@app.on_message(filters.command(["ping", f"ping@{BOT_USERNAME}"]))
async def ping_cmd(client, message):
    await message.reply(f"<blockquote><emoji id=5373146461061551826>🟢</emoji> <b>Alive</b> <emoji id=5372981702439583899>⏰</emoji> {TIMERS[message.chat.id]}s</blockquote>")

async def main():
    print("🚀 Starting SHIV MEDIA DEFENDER - RENDER")
    await app.start()
    print("✅ Bot Client Started")
    await set_commands()
    print(f"✅ Bot @{BOT_USERNAME} Running - Premium Active")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
