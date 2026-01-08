import os
import asyncio
from quart import Quart, redirect, render_template_string
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================
# 💎 PREMIUM SETTINGS (Updated)
# ==========================================
API_ID = 30646544
API_HASH = "d2f5e1abde0d56694941f965aff8d987"
BOT_TOKEN = "8357960011:AAHqtS6CPh7kCY_7BZYHxIOnZQEuGtqLTns"

# Aapki MongoDB (Data Save Karne ke liye)
MONGO_URL = "mongodb+srv://ramu9045690509_db_user:J1g4r069@jigar069.ud3vuw7.mongodb.net/?appName=Jigar069"

# Channel Details
CHANNEL_USERNAME = "Myfirstvideochannel"  # Bina @ ke
CHANNEL_LINK = "https://t.me/Myfirstvideochannel"

# 👑 OWNER ID (Updated: 7846018094)
ADMIN_ID = 7846018094 

DOMAIN = "https://bot-builder--markzubarwark.replit.app"
AD_LINK = "https://otieu.com/4/10330643"
DELETE_TIME = 3600  # 1 Ghanta

# ==========================================
# 💾 DATABASE CONNECT
# ==========================================
try:
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client['VideoBotDB']
    users_collection = db['users']
    print("✅ MongoDB Connected (Premium Mode)")
except Exception as e:
    print(f"❌ DB Error: {e}")

async def add_user(user_id):
    try:
        await users_collection.update_one({'user_id': user_id}, {'$set': {'user_id': user_id}}, upsert=True)
    except: pass

# ==========================================
# 🎨 HTML PLAYER (Dark Premium Theme)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Premium Player</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #0f0f0f; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: #1a1a1a; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: center; width: 80%; max-width: 400px; }
        .btn { background: linear-gradient(45deg, #ff0000, #c90000); color: white; padding: 12px 25px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 16px; margin-top: 20px; border: none; cursor: pointer; display: inline-block; width: 80%; }
        .success { background: linear-gradient(45deg, #00b09b, #96c93d); display: none; }
        h2 { margin: 0 0 10px 0; font-size: 22px; }
        p { color: #888; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 Secure Streaming</h2>
        <p>Click below to verify and watch in HD</p>
        
        <button id="fakeBtn" class="btn" onclick="openAd()">▶ PLAY VIDEO</button>
        
        <a id="realBtn" class="btn success" href="{{ tg_link }}">🚀 OPEN APP</a>
    </div>

    <script>
        var adUrl = "{{ ad_link }}";
        function openAd() {
            window.open(adUrl, '_blank');
            document.getElementById('fakeBtn').style.display = 'none';
            document.getElementById('realBtn').style.display = 'block';
        }
    </script>
</body>
</html>
"""

# ==========================================
# ⚙️ ENGINE START
# ==========================================
app = Quart(__name__)
bot = Client("PremiumBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.route('/')
async def home(): return "<h1>💎 Premium Bot is Live</h1>"

@app.route('/watch/<int:msg_id>')
async def watch(msg_id):
    link = f"https://t.me/{CHANNEL_USERNAME}/{msg_id}"
    return await render_template_string(HTML_PAGE, tg_link=link, ad_link=AD_LINK)

# ==========================================
# 🤖 FEATURES & LOGIC
# ==========================================

async def not_subscribed(client, message):
    if not CHANNEL_USERNAME: return False
    try:
        user = await client.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if user.status in ['kicked', 'left', 'banned']: return True
    except: return True
    return False

@bot.on_message(filters.command("start"))
async def start(client, message):
    await add_user(message.from_user.id)
    if await not_subscribed(client, message):
        # Premium Force Sub Message with Button
        await message.reply_text(
            "🔒 **Access Locked!**\n\nPlease join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Join Channel", url=CHANNEL_LINK)]])
        )
        return
    await message.reply_text("👋 **Welcome Boss!**\nSend me any video/file to generate a premium link.")

# 📢 Broadcast (Sirf Aapke liye)
@bot.on_message(filters.command("broadcast") & filters.reply & filters.user(ADMIN_ID))
async def broadcast(client, message):
    users = users_collection.find({})
    msg = await message.reply_text("🚀 Sending Broadcast...")
    sent, failed = 0, 0
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            sent += 1
            await asyncio.sleep(0.1)
        except: failed += 1
    await msg.edit_text(f"✅ **Complete!**\nSent: {sent} | Failed: {failed}")

# 🎬 Video Handler (Stylish Post Logic)
@bot.on_message(filters.video | filters.document)
async def handle_video(client, message):
    if await not_subscribed(client, message):
        await message.reply_text("⚠️ Join Channel First!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Now", url=CHANNEL_LINK)]]))
        return

    try:
        # Step 1: Channel me "COPY" karo (Forward nahi)
        # Isse "Forwarded from" tag hatt jayega aur post original lagegi
        # Caption me hum File ka asli naam daal rahe hain
        file_caption = f"🎬 **{message.video.file_name if message.video else 'Exclusive Video'}**\n\n💾 Size: Premium Quality\n📢 Uploaded by: {CHANNEL_USERNAME}"
        
        sent_msg = await message.copy(
            CHANNEL_USERNAME, 
            caption=file_caption
        )
        
        # Step 2: Link Generate
        stream_link = f"{DOMAIN}/watch/{sent_msg.id}"
        
        # Step 3: User ko "Button" wala reply bhejo (Stylish)
        await message.reply_text(
            f"<b>✅ LINK GENERATED</b>\n\n"
            f"🎬 <b>Title:</b> {message.video.file_name if message.video else 'Video'}\n"
            f"⚠️ <b>Expires in:</b> 1 Hour\n\n"
            f"👇 <b>Click below to watch:</b>",
            parse_mode=errors.enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Watch / Download 🚀", url=stream_link)],
                [InlineKeyboardButton("📺 Share Channel", url=CHANNEL_LINK)]
            ]),
            quote=True
        )
        
        # Step 4: Auto Delete
        await asyncio.sleep(DELETE_TIME)
        # Note: Hum user ka message delete nahi kar rahe taki usse yaad rahe
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# ==========================================
# 🚀 RUNNER
# ==========================================
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start())
    app.run(host='0.0.0.0', port=8080, loop=loop)
                
