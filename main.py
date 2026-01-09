import os
import asyncio
from quart import Quart, render_template_string
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================
# 💎 CONFIGURATION (SETTING)
# ==========================================

# 1. Telegram API Details
API_ID = 30646544
API_HASH = "d2f5e1abde0d56694941f965aff8d987"
BOT_TOKEN = "8357960011:AAHqtS6CPh7kCY_7BZYHxIOnZQEuGtqLTns"

# 2. Database (MongoDB)
MONGO_URL = "mongodb+srv://ramu9045690509_db_user:J1g4r069@jigar069.ud3vuw7.mongodb.net/?appName=Jigar069"

# 3. Channel Details (Force Sub & Storage)
CHANNEL_USERNAME = "Myfirstvideochannel"
CHANNEL_LINK = "https://t.me/Myfirstvideochannel"

# 4. Owner ID (Broadcast ke liye)
ADMIN_ID = 7846018094 

# 5. Domain (Aapka Asli Koyeb Link)
# Maine screenshot se aapka sahi link nikal liya hai:
DOMAIN = "https://large-zonda-jigar069-de4dac4c.koyeb.app"

# 6. Other Settings
AD_LINK = "https://otieu.com/4/10330643"
DELETE_TIME = 3600  # Link 1 ghante baad expire hoga

# ==========================================
# 💾 DATABASE CONNECTION
# ==========================================
print("🔄 Connecting to Database...")
try:
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client['VideoBotDB']
    users_collection = db['users']
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ Database Error: {e}")

async def add_user(user_id):
    """User ko database mein add karne ka function"""
    try:
        await users_collection.update_one(
            {'user_id': user_id}, 
            {'$set': {'user_id': user_id}}, 
            upsert=True
        )
    except Exception as e:
        print(f"User Add Error: {e}")

# ==========================================
# 🎨 HTML PLAYER TEMPLATE (Premium Design)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Premium Video Player</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            background: #0f0f0f; 
            color: #fff; 
            font-family: 'Segoe UI', sans-serif; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            margin: 0; 
        }
        .card { 
            background: #1a1a1a; 
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
            text-align: center; 
            width: 85%; 
            max-width: 400px; 
        }
        h2 { margin: 0 0 10px 0; color: #fff; font-size: 24px; }
        p { color: #aaa; font-size: 14px; margin-bottom: 25px; }
        
        /* Buttons Design */
        .btn { 
            background: linear-gradient(45deg, #ff0000, #c90000); 
            color: white; 
            padding: 14px 30px; 
            border-radius: 50px; 
            text-decoration: none; 
            font-weight: bold; 
            font-size: 16px; 
            border: none; 
            cursor: pointer; 
            display: inline-block; 
            width: 100%; 
            box-sizing: border-box;
            transition: transform 0.2s;
        }
        .btn:active { transform: scale(0.95); }
        
        .success { 
            background: linear-gradient(45deg, #00b09b, #96c93d); 
            display: none; /* Pehle chhupa rahega */
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎬 Ready to Watch</h2>
        <p>Verified Secure Stream • High Quality</p>
        
        <button id="fakeBtn" class="btn" onclick="openAd()">▶ PLAY VIDEO</button>
        
        <a id="realBtn" class="btn success" href="{{ tg_link }}">🚀 OPEN IN APP</a>
    </div>

    <script>
        var adUrl = "{{ ad_link }}";
        
        function openAd() {
            // Ad naye tab mein khulega
            window.open(adUrl, '_blank');
            
            // Button badal jayega
            document.getElementById('fakeBtn').style.display = 'none';
            document.getElementById('realBtn').style.display = 'block';
        }
    </script>
</body>
</html>
"""

# ==========================================
# ⚙️ BOT & SERVER SETUP
# ==========================================
app = Quart(__name__)

# Bot Setup with IPv6 Disabled (Fixes Network Error)
bot = Client(
    "PremiumBot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    ipv6=False  # <--- VERY IMPORTANT FOR KOYEB
)

# --- Server Routes ---
@app.route('/')
async def home():
    return "<h1>✅ Bot is Running Successfully on Port 8000</h1>"

@app.route('/watch/<int:msg_id>')
async def watch(msg_id):
    # Link banata hai jo Telegram post par le jayega
    link = f"https://t.me/{CHANNEL_USERNAME}/{msg_id}"
    return await render_template_string(HTML_PAGE, tg_link=link, ad_link=AD_LINK)

# ==========================================
# 🤖 BOT COMMANDS & LOGIC
# ==========================================

async def not_subscribed(client, message):
    """Check karta hai ki user ne channel join kiya hai ya nahi"""
    if not CHANNEL_USERNAME: return False
    try:
        user = await client.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if user.status in ['kicked', 'left', 'banned']: return True
    except:
        return True
    return False

@bot.on_message(filters.command("start"))
async def start(client, message):
    # User ko DB mein save karo
    await add_user(message.from_user.id)
    
    # Force Sub Check
    if await not_subscribed(client, message):
        await message.reply_text(
            "🔒 **Access Denied!**\n\nIs Bot ko use karne ke liye Channel join karna zaroori hai.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔓 Join Channel Now", url=CHANNEL_LINK)]
            ])
        )
        return
        
    await message.reply_text(
        "👋 **Namaste Boss!**\n\n"
        "Main ready hu! Koi bhi **Video** ya **File** bhejo, main uska "
        "High-Speed Link bana dunga."
    )

@bot.on_message(filters.command("broadcast") & filters.reply & filters.user(ADMIN_ID))
async def broadcast(client, message):
    """Sirf Admin ke liye: Sab users ko message bhejne ka feature"""
    msg = await message.reply_text("🚀 Broadcast Shuru ho raha hai...")
    users = users_collection.find({})
    sent = 0
    failed = 0
    
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            sent += 1
            await asyncio.sleep(0.1) # Floodwait se bachne ke liye
        except:
            failed += 1
            
    await msg.edit_text(f"✅ **Broadcast Khatam!**\n\nSent: {sent}\nFailed: {failed}")

@bot.on_message(filters.video | filters.document)
async def handle_video(client, message):
    # Force Sub Check
    if await not_subscribed(client, message):
        await message.reply_text(
            "⚠️ Please Channel Join Karein!", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)]])
        )
        return

    try:
        msg_notify = await message.reply_text("🔄 **Processing...**")
        
        # 1. Channel par 'Copy' karo (Forward tag hatane ke liye)
        file_name = message.video.file_name if message.video else message.document.file_name
        caption_text = f"🎬 **{file_name}**\n\n💾 Quality: Original\n📢 Uploaded by: @{CHANNEL_USERNAME}"
        
        sent_msg = await message.copy(
            CHANNEL_USERNAME, 
            caption=caption_text
        )
        
        # 2. Link Generate karo
        stream_link = f"{DOMAIN}/watch/{sent_msg.id}"
        
        # 3. User ko Stylish Reply bhejo
        await msg_notify.delete()
        await message.reply_text(
            f"<b>✅ LINK GENERATED SUCCESSFULLY</b>\n\n"
            f"📂 <b>File:</b> {file_name}\n"
            f"🔗 <b>Link:</b> Public Stream\n\n"
            f"👇 <b>Link par click karke dekhein:</b>",
            parse_mode=errors.enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Watch / Download 🚀", url=stream_link)],
                [InlineKeyboardButton("📺 Share Channel", url=CHANNEL_LINK)]
            ]),
            quote=True
        )
        
        # 4. Auto Delete (Privacy ke liye)
        await asyncio.sleep(DELETE_TIME)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}\n\n(Tip: Check karein ki Bot channel ka Admin hai ya nahi)")

# ==========================================
# 🚀 SERVER START (PORT 8000)
# ==========================================
if __name__ == '__main__':
    print("🔥 Bot Starting on Port 8000...")
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start())
    
    # 👇 KOYEB KE LIYE SABSE ZAROORI LINE (PORT 8000)
    app.run(host='0.0.0.0', port=8000, loop=loop)
  
