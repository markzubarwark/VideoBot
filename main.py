import os
import asyncio
from quart import Quart, render_template_string
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# ====================================================================
# 1. SETTINGS (AAPKI DETAILS)
# ====================================================================
API_ID = 30646544
API_HASH = "d2f5e1abde0d56694941f965aff8d987"
BOT_TOKEN = "8357960011:AAHqtS6CPh7kCY_7BZYHxIOnZQEuGtqLTns"

# Database Link
MONGO_URL = "mongodb+srv://ramu9045690509_db_user:J1g4r069@jigar069.ud3vuw7.mongodb.net/?appName=Jigar069"

# Channel Details
CHANNEL_USERNAME = "Myfirstvideochannel"
CHANNEL_LINK = "https://t.me/Myfirstvideochannel"
ADMIN_ID = 7846018094 

# ✅ DOMAIN (Aapka Naya Link - Updated)
DOMAIN = "https://videobot-finel.onrender.com"
AD_LINK = "https://otieu.com/4/10330643"

# ====================================================================
# 2. DATABASE CONNECTION
# ====================================================================
print("🔄 Connecting to Database...")
try:
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client['VideoBotDB']
    users_collection = db['users']
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ Database Error: {e}")

async def add_user(user_id):
    try:
        await users_collection.update_one({'user_id': user_id}, {'$set': {'user_id': user_id}}, upsert=True)
    except: pass

# ====================================================================
# 3. WEBSITE HTML (PLAYER)
# ====================================================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Video Player</title>
    <style>
        body { background-color: #0f0f0f; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { background: #1e1e1e; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 90%; max-width: 400px; }
        .btn { display: block; width: 100%; padding: 15px; margin: 10px 0; border-radius: 50px; border: none; font-size: 16px; font-weight: bold; cursor: pointer; text-decoration: none; color: white; transition: 0.3s; box-sizing: border-box; }
        #fakeBtn { background: linear-gradient(45deg, #ff416c, #ff4b2b); }
        #realBtn { background: linear-gradient(45deg, #00b09b, #96c93d); display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 Ready to Watch</h2>
        <p>Verified Stream • High Quality</p>
        <button id="fakeBtn" class="btn" onclick="openAd()">▶ PLAY VIDEO</button>
        <a id="realBtn" class="btn" href="{{ tg_link }}">🚀 OPEN TELEGRAM</a>
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

# ====================================================================
# 4. BOT SETUP
# ====================================================================
app = Quart(__name__)

# in_memory=True lagaya hai taaki permission error na aaye
bot = Client(
    "VideoBot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ====================================================================
# 5. ROUTES (WEBSITE)
# ====================================================================
@app.route('/')
async def home():
    return "<h1>✅ Bot is Live & Port Fixed!</h1>"

@app.route('/watch/<int:msg_id>')
async def watch(msg_id):
    link = f"https://t.me/{CHANNEL_USERNAME}/{msg_id}"
    return await render_template_string(HTML_PAGE, tg_link=link, ad_link=AD_LINK)

# ====================================================================
# 6. BOT COMMANDS
# ====================================================================

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
        await message.reply_text(
            "🔒 **Access Denied!**\nJoin Channel first.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)]])
        )
        return
    await message.reply_text("👋 **Welcome Boss!**\nSend me any video.")

@bot.on_message(filters.command("broadcast") & filters.reply & filters.user(ADMIN_ID))
async def broadcast(client, message):
    msg = await message.reply_text("🚀 Broadcasting...")
    users = users_collection.find({})
    sent, failed = 0, 0
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            sent += 1
            await asyncio.sleep(0.1)
        except: failed += 1
    await msg.edit_text(f"✅ **Done!**\nSent: {sent} | Failed: {failed}")

@bot.on_message(filters.video | filters.document)
async def handle_video(client, message):
    if await not_subscribed(client, message):
        await message.reply_text("⚠️ Join Channel First!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Now", url=CHANNEL_LINK)]]))
        return
    try:
        notify = await message.reply_text("🔄 **Processing...**")
        file_name = message.video.file_name if message.video else "Video"
        
        # Channel par copy
        sent_msg = await message.copy(CHANNEL_USERNAME, caption=f"🎬 **{file_name}**")
        
        # Sahi Link Generate hoga
        stream_link = f"{DOMAIN}/watch/{sent_msg.id}"
        
        await notify.delete()
        await message.reply_text(
            f"<b>✅ LINK GENERATED</b>\n👇 <b>Click to Watch:</b>",
            parse_mode=errors.enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Watch / Download 🚀", url=stream_link)],
                [InlineKeyboardButton("📺 Channel", url=CHANNEL_LINK)]
            ]),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# ====================================================================
# 7. SERVER STARTUP (PORT FIX)
# ====================================================================

@app.before_serving
async def startup():
    print("🚀 Bot Starting...")
    await bot.start()

@app.after_serving
async def cleanup():
    print("😴 Bot Stopping...")
    try:
        await bot.stop()
    except: pass

# ✅ YE HAI PORT FIX (ISKE BINA RENDER PAR NAHI CHALEGA)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
        
