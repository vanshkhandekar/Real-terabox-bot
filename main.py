import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

app = Client(
    "TeraboxBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

USERS = {}
PREMIUM_USERS = set([config.OWNER_ID])  # Owner always premium

def is_premium(user_id):
    return user_id in PREMIUM_USERS

async def force_join_check(client, message):
    """Force join channel checker"""
    if config.FORCE_CHANNEL:
        try:
            user = await client.get_chat_member(f"@{config.FORCE_CHANNEL}", message.from_user.id)
            if user.status == "left":
                await message.reply_text(
                    f"🚫 Bot use karne ke liye pehle @{config.FORCE_CHANNEL} join karo.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{config.FORCE_CHANNEL}")]]
                    )
                )
                return False
        except Exception:
            # If user not found in channel, ask to join
            await message.reply_text(
                f"🚫 Bot use karne ke liye pehle @{config.FORCE_CHANNEL} join karo.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{config.FORCE_CHANNEL}")]]
                )
            )
            return False
    return True

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    if not await force_join_check(client, message):
        return
    name = message.from_user.first_name
    text = (
        f"👋 Welcome {name}!\n\n"
        f"🔸 Normal user limit: {config.NORMAL_DAILY_LIMIT} links/day\n"
        f"🔸 Premium user: Unlimited links & bulk\n\n"
        f"💳 Premium lena hai toh niche payment pe tap karo!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy Premium", url=config.PAYMENT_CHANNEL)],
        [InlineKeyboardButton("📞 Contact Owner", url=f"https://t.me/{config.OWNER_USERNAME}")]
    ])
    await message.reply_text(text, reply_markup=keyboard)

@app.on_message(filters.command("premium"))
async def premium_cmd(client, message):
    if not await force_join_check(client, message):
        return
    text = (
        "💳 Premium Plans:\n"
        "• 1 Month Unlimited: ₹---\n"
        "• Bulk up to 5 links at once\n\n"
        "Payment lene ke liye niche dabaye, aur hone ke baad owner se contact karein."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay/Upgrade", url=config.PAYMENT_CHANNEL)],
        [InlineKeyboardButton("📞 Owner Contact", url=f"https://t.me/{config.OWNER_USERNAME}")]
    ])
    await message.reply_text(text, reply_markup=keyboard)

@app.on_message(filters.text & ~filters.command(["start", "premium"]))
async def handle_links(client, message):
    if not await force_join_check(client, message):
        return
    uid = message.from_user.id
    USERS.setdefault(uid, 0)
    USERS[uid] += 1
    # Limit check for normal user
    if not is_premium(uid) and USERS[uid] > config.NORMAL_DAILY_LIMIT:
        await message.reply_text(
            "❌ Daily limit khatam! Premium lo ya kal try karo.\nPayment lene ke liye /premium dabaye."
        )
        return
    link = message.text.strip()
    # Simulate download/upload -- replace yahan Terabox logic jab ho
    sent = await message.reply_text(
        f"⏳ Downloading from: {link}\n(This is a simulated download for demo.)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📞 Help", url=f"https://t.me/{config.OWNER_USERNAME}")
        ]])
    )
    # Dummy file sending (replace with actual download/upload logic)
    await asyncio.sleep(3)
    await message.reply_document("sample.mp4", caption="🎬 Sample File\n💾 Size: 10MB\n⏱ 00:30")
    # Auto delete after timer
    await asyncio.sleep(config.AUTO_DELETE_TIME)
    await sent.delete()

app.run()
