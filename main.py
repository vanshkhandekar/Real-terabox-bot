import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from datetime import datetime, timedelta

app = Client(
    "TeraboxBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

USERS = {}
PREMIUM_USERS = {}  # user_id: expiry_datetime

def is_premium(user_id):
    exp = PREMIUM_USERS.get(user_id)
    if exp and exp > datetime.now():
        return True
    return False

def add_premium(user_id, plan):
    """Manually call this function as owner to set user's premium plan."""
    now = datetime.now()
    if plan == '1m':
        expiry = now + timedelta(days=30)
    elif plan == '6m':
        expiry = now + timedelta(days=182)
    elif plan == '1y':
        expiry = now + timedelta(days=365)
    else:
        return False
    PREMIUM_USERS[user_id] = expiry
    return expiry

async def force_join_check(client, message):
    if config.FORCE_CHANNEL:
        try:
            user = await client.get_chat_member(f"@{config.FORCE_CHANNEL}", message.from_user.id)
            if user.status == "left":
                await message.reply_text(
                    f"🚫 Please join @{config.FORCE_CHANNEL} to use this bot.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{config.FORCE_CHANNEL}")]]
                    )
                )
                return False
        except Exception:
            await message.reply_text(
                f"🚫 Please join @{config.FORCE_CHANNEL} to use this bot.",
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
    # ENGLISH WELCOME
    text = (
        f"👋 Welcome {message.from_user.first_name}!\n\n"
        "This is the fastest Terabox download bot.\n"
        "Send any Terabox link and I will give you the download instantly!\n"
        f"\n🔸 Normal user limit: {config.NORMAL_DAILY_LIMIT} links/day"
        "\n🔸 Premium users: Unlimited downloads & bulk links\n\n"
        "💳 To buy premium, click PAY below & join @franky_payment. Scan UPI QR and DM the owner for activation!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 PAY / Join Payment Channel", url=f"https://t.me/{config.PAYMENT_CHANNEL}")],
        [InlineKeyboardButton("📞 Contact Owner", url=f"https://t.me/{config.OWNER_USERNAME}")]
    ])
    await message.reply_text(text, reply_markup=keyboard)


@app.on_message(filters.command("premium"))
async def premium_cmd(client, message):
    if not await force_join_check(client, message):
        return
    # Premium Plan Info
    text = (
        "💳 Premium Plans:\n"
        "• 1 Month: ₹---\n"
        "• 6 Months: ₹---\n"
        "• 1 Year: ₹---\n"
        "Benefits: Unlimited links, bulk up to 5 links.\n\n"
        "For payment, click PAY below & join @franky_payment.\nScan UPI QR posted there.\nAfter payment, contact owner with screenshot.\nOwner will activate your premium plan."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 PAY / Join @franky_payment", url=f"https://t.me/{config.PAYMENT_CHANNEL}")],
        [InlineKeyboardButton("📞 Contact Owner", url=f"https://t.me/{config.OWNER_USERNAME}")]
    ])
    await message.reply_text(text, reply_markup=keyboard)

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    help_text = (
        "**Help Menu**\n\n"
        "• /start - Welcome message\n"
        "• /premium - Premium plans & payment info\n"
        "• /stats - Users & premium info\n"
        "• /about - Bot & owner info\n"
        "• /contact - Talk to owner\n"
        "Send any Terabox link, bot will download for you.\n"
        "To get premium, join @franky_payment and DM owner after payment."
    )
    await message.reply_text(help_text)

@app.on_message(filters.command("stats"))
async def stats_cmd(client, message):
    total_users = len(USERS)
    premium_count = sum(1 for v in PREMIUM_USERS.values() if v > datetime.now())
    stats_text = (
        f"**Bot Stats**\n"
        f"- Total users: `{total_users}`\n"
        f"- Premium users: `{premium_count}`\n"
    )
    await message.reply_text(stats_text)

@app.on_message(filters.command("about"))
async def about_cmd(client, message):
    about_text = (
        "**About This Bot:**\n"
        "- Terabox links downloader\n"
        f"- Owner: @{config.OWNER_USERNAME}\n"
        f"- Payment channel: @{config.PAYMENT_CHANNEL}\n"
    )
    await message.reply_text(about_text)

@app.on_message(filters.command("contact"))
async def contact_cmd(client, message):
    await message.reply_text(
        f"📞 Owner Contact: [Click Here](https://t.me/{config.OWNER_USERNAME})",
        disable_web_page_preview=True
    )

# Owner-only command to add premium (for your use)
@app.on_message(filters.command("addpremium") & filters.user(config.OWNER_ID))
async def add_premium_cmd(client, message):
    try:
        params = message.text.split()
        if len(params) < 3:
            await message.reply("Usage:\n/addpremium [user_id] [1m/6m/1y]")
            return
        user_id = int(params[1])
        plan = params[2]
        expiry = add_premium(user_id, plan)
        if expiry:
            await message.reply(f"Premium activated for user `{user_id}` till `{expiry.strftime('%Y-%m-%d %H:%M')}`")
        else:
            await message.reply("Invalid plan! Use: 1m, 6m, or 1y")
    except Exception as e:
        await message.reply(str(e))

@app.on_message(filters.text & ~filters.command(["start", "premium", "help", "stats", "about", "contact", "addpremium"]))
async def handle_links(client, message):
    if not await force_join_check(client, message):
        return
    uid = message.from_user.id
    USERS.setdefault(uid, 0)
    USERS[uid] += 1
    if not is_premium(uid) and USERS[uid] > config.NORMAL_DAILY_LIMIT:
        await message.reply_text(
            "❌ Daily limit is over! Buy premium using /premium or try tomorrow."
        )
        return
    link = message.text.strip()
    # Simulate download/upload
    sent = await message.reply_text(
        f"⏳ Downloading from: {link}\n(This is a simulated download for demo.)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Payment Channel", url=f"https://t.me/{config.PAYMENT_CHANNEL}")
        ]])
    )
    # Dummy file sending (replace with actual download logic)
    await asyncio.sleep(2)
    await message.reply_document("sample.mp4", caption="🎬 Sample File\n💾 Size: 10MB\n⏱ 00:30")
    await asyncio.sleep(config.AUTO_DELETE_TIME)
    await sent.delete()

app.run()
