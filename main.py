import os
import asyncio
from quart import Quart, render_template_string
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# ====================================================================
# 🛠️ CONFIGURATION SECTION (SETTINGS)
# ====================================================================

# 1. Telegram API (Aapka account login)
API_ID = 30646544
API_HASH = "d2f5e1abde0d56694941f965aff8d987"
BOT_TOKEN = "8357960011:AAHqtS6CPh7kCY_7BZYHxIOnZQEuGtqLTns"

# 2. Database Connection (MongoDB)
MONGO_URL = "mongodb+srv://ramu9045690509_db_user:J1g4r069@jigar069.ud3vuw7.mongodb.net/?appName=Jigar069"

# 3. Channel Details (Is channel ko join karna zaroori hoga)
CHANNEL_USERNAME = "Myfirstvideochannel"
CHANNEL_LINK = "https://t.me/Myfirstvideochannel"

# 4. Admin ID (Sirf aap broadcast kar payenge)
ADMIN_ID = 7846018094 

# 5. Website Domain (Koyeb URL)
# Maine screenshot se aapka sahi link nikal kar yahan laga diya hai.
# Ab 'Watch' button dabane par error nahi aayega.
DOMAIN = "https://large-zonda-jigar069-de4dac4c.koyeb.app"

# 6. Ad Link & Timer
AD_LINK = "https://otieu.com/4/10330643"
DELETE_TIME = 3600  # Link 1 ghante baad expire hoga

# ====================================================================
# 💾 DATABASE LOGIC
# ====================================================================

print("🔄 Database se connect ho raha hai...")
try:
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client['VideoBotDB']
    users_collection = db['users']
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ Database Error: {e}")

async def add_user(user_id):
    """Naye user ko database mein save karta hai"""
    try:
        await users_collection.update_one(
            {'user_id': user_id}, 
            {'$set': {'user_id': user_id}}, 
            upsert=True
        )
    except Exception as e:
        pass

# ====================================================================
# 🎨 HTML PLAYER (WEBSITE DESIGN)
# ====================================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Video Player</title>
    <style>
        body { 
            background-color: #0f0f0f; 
            color: white; 
            font-family: sans-serif; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            margin: 0; 
        }
        .container { 
            background: #1e1e1e; 
            padding: 30px; 
            border-radius: 20px; 
            text-align: center; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
            max-width: 90%; 
            width: 350px; 
        }
        h2 { margin-top: 0; color: #fff; }
        p { color: #aaa; font-size: 14px; margin-bottom: 25px; }
        
        .btn { 
            display: block; 
            width: 100%; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 50px; 
            border: none; 
            font-size: 16px; 
            font-weight: bold; 
            cursor: pointer; 
            text-decoration: none; 
            color: white; 
            transition: 0.3s;
            box-sizing: border-box;
        }
        
        /* Fake Button Style */
        #fakeBtn { 
            background: linear-gradient(45deg, #ff416c, #ff4b2b); 
        }
        
        /* Real Button Style */
        #realBtn { 
            background: linear-gradient(45deg, #00b09b, #96c93d); 
            display: none; /* Starting mein chhupa rahega */
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 Ready to Watch</h2>
        <p>Click the button below to stream in HD quality.</p>
        
        <button id="fakeBtn" class="btn" onclick="openAd()">▶ PLAY VIDEO</button>
        
        <a id="realBtn" class="btn" href="{{ tg_link }}">🚀 OPEN TELEGRAM</a>
    </div>

    <script>
        // Server se Ad ka link yahan aayega
        var adUrl = "{{ ad_link }}";
        
        function openAd() {
            // 1. Ad naye tab mein khulega
            window.open(adUrl, '_blank');
            
            // 2. Fake button gayab, Real button show
            document.getElementById('fakeBtn').style.display = 'none';
            document.getElementById('realBtn').style.display = 'block';
        }
    </script>
</body>
</html>
"""

# ====================================================================
# ⚙️ BOT INITIALIZATION
# ====================================================================

app = Quart(__name__)

# IPv6 False kiya hai taaki 'Network Error' na aaye
bot = Client(
    "VideoBot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    ipv6=False  
)

# --- Web Routes (Website ke pages) ---

@app.route('/')
async def home():
    return "<h1>✅ Bot is Running Successfully on Koyeb!</h1>"

@app.route('/watch/<int:msg_id>')
async def watch(msg_id):
    # Telegram post ka link banata hai
    link = f"https://t.me/{CHANNEL_USERNAME}/{msg_id}"
    return await render_template_string(HTML_PAGE, tg_link=link, ad_link=AD_LINK)

# ====================================================================
# 🤖 BOT COMMANDS (FEATURES)
# ====================================================================

async def check_joined(client, message):
    """Check karta hai ki user ne channel join kiya hai ya nahi"""
    if not CHANNEL_USERNAME: return False
    try:
        user = await client.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if user.status in ['kicked', 'left', 'banned']: return True
    except:
        return True
    return False

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await add_user(message.from_user.id)
    
    # Join Check
    if await check_joined(client, message):
        await message.reply_text(
            "🔒 **Access Denied!**\n\nPehle Channel Join karein, fir 'Try Again' dabayein.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.me.username}?start=start")]
            ])
        )
        return
        
    await message.reply_text(
        "👋 **Hello Boss!**\n\n"
        "Main ready hu. Mujhe koi bhi **Video** bhejiye, main uska link bana dunga."
    )

@bot.on_message(filters.video | filters.document)
async def process_video(client, message):
    # Join Check
    if await check_joined(client, message):
        await message.reply_text("⚠️ Pehle Channel Join Karein!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)]]))
        return

    try:
        wait_msg = await message.reply_text("🔄 **Processing...**")
        
        # 1. Video ko Channel par copy karo (Forward tag hatane ke liye)
        filename = message.video.file_name if message.video else "Video File"
        caption = f"🎬 **{filename}**\n\n💾 Quality: Original\n📢 Uploaded by: @{CHANNEL_USERNAME}"
        
        copied_msg = await message.copy(CHANNEL_USERNAME, caption=caption)
        
        # 2. Link Generate karo
        # (Yahan 'DOMAIN' variable use ho raha hai jo humne upar set kiya tha)
        stream_link = f"{DOMAIN}/watch/{copied_msg.id}"
        
        # 3. User ko Link bhejo
        await wait_msg.delete()
        await message.reply_text(
            f"<b>✅ LINK GENERATED</b>\n\n"
            f"📂 <b>File:</b> {filename}\n"
            f"🔗 <b>Link:</b> Public Stream Link\n\n"
            f"👇 <b>Niche click karke dekhein:</b>",
            parse_mode=errors.enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Watch / Download 🚀", url=stream_link)],
                [InlineKeyboardButton("📺 Channel", url=CHANNEL_LINK)]
            ]),
            quote=True
        )
        
        # 4. Privacy ke liye link wala message delete karo (Optional)
        await asyncio.sleep(DELETE_TIME)
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}\n(Kya Bot Channel ka Admin hai?)")

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID) & filters.reply)
async def broadcast_command(client, message):
    """Admin sabko message bhej sakta hai"""
    status_msg = await message.reply_text("🚀 Sending Broadcast...")
    users = users_collection.find({})
    success = 0
    failed = 0
    
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            success += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
            
    await status_msg.edit_text(f"✅ **Broadcast Complete!**\n\nSent: {success}\nFailed: {failed}")

# ====================================================================
# 🔥 MAIN EXECUTION (PORT 8000)
# ====================================================================

if __name__ == '__main__':
    print("🔥 Bot Starting on Port 8000...")
    
    # Loop setup
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start())
    
    # KOYEB PORT 8000 CONFIGURATION
    app.run(host='0.0.0.0', port=8000, loop=loop)
                                      
