import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from terabox_dl import Terabox
import config

app = Client(
    "TeraboxBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

USERS = {}
TERABOX_DOMAINS = ["terabox.com", "terabox.app", "tbfiles.com"]

def is_terabox_link(text):
    return any(domain in text for domain in TERABOX_DOMAINS)

async def force_join_check(client, message):
    if config.FORCE_CHANNEL:
        try:
            user = await client.get_chat_member(f"@{config.FORCE_CHANNEL}", message.from_user.id)
            if user.status == "left":
                await message.reply_text(
                    f"🚫 Please join @{config.FORCE_CHANNEL} to use this bot.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📢 Join", url=f"https://t.me/{config.FORCE_CHANNEL}")]]
                    )
                )
                return False
        except:
            await message.reply_text(
                f"🚫 Please join @{config.FORCE_CHANNEL} to use this bot.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📢 Join", url=f"https://t.me/{config.FORCE_CHANNEL}")]]
                )
            )
            return False
    return True

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    if not await force_join_check(client, message):
        return
    text = (
        f"👋 Welcome {message.from_user.first_name}!\n\n"
        "Send any Terabox link (terabox.com/app/tbfiles.com) and I'll fetch your REAL video/file!\n"
        f"\n🔸 Normal user limit: {config.NORMAL_DAILY_LIMIT} links/day"
        "\n🔸 Premium users: Unlimited\n"
        "💳 To buy premium, join @franky_payment (UPI QR) & DM owner."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Payment Channel", url=f"https://t.me/{config.PAYMENT_CHANNEL}")],
        [InlineKeyboardButton("📞 Owner", url=f"https://t.me/{config.OWNER_USERNAME}")]
    ])
    await message.reply_text(text, reply_markup=keyboard)

@app.on_message(filters.text & ~filters.command(["start"]))
async def links_handler(client, message):
    if not await force_join_check(client, message):
        return
    user_id = message.from_user.id
    USERS.setdefault(user_id, 0)
    USERS[user_id] += 1
    if USERS[user_id] > config.NORMAL_DAILY_LIMIT:
        await message.reply_text("❌ Limit over! Buy premium using /premium or try tomorrow.")
        return
    link = message.text.strip()
    if not is_terabox_link(link):
        await message.reply_text("❌ Only valid Terabox links supported!")
        return
    try:
        m = await message.reply_text("⏳ Downloading from Terabox, please wait...")
        tb = Terabox(link)
        file_path = tb.download()
        await message.reply_document(file_path, caption="🎬 Downloaded from Terabox!")
        await m.edit_text("✅ File sent!")
        os.remove(file_path)
    except Exception as e:
        await message.reply_text(f"❌ Download Error: {e}")

app.run()
