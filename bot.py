import os
import threading
import http.server
import socketserver
import telebot
from yt_dlp import YoutubeDL

# =======================================================
# ၁။ Render.com အခမဲ့ဆာဗာအတွက် အချက်ပြစနစ် (Dummy Server)
# =======================================================
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Dummy server running on port {PORT}")
        httpd.serve_forever()

# ဆာဗာကို နောက်ကွယ်ကနေ သီးသန့် Background Thread အနေနဲ့ စပတ်ထားခြင်း
threading.Thread(target=run_dummy_server, daemon=True).start()


# =======================================================
# ၂။ TELEGRAM BOT CONFIGURATION (ပြင်ဆင်ရန်နေရာ)
# =======================================================
# ⚠️ အရေးကြီး - အောက်ပါနေရာတွင် သင့်ရဲ့ Bot Token ကို သေချာထည့်ပေးပါ (ကွက်လပ် လုံးဝ မပါရပါ)
BOT_TOKEN = "8946763002:AAGzWsyC6-Gvt_kIgRHmSv8rtAqcXF-pQ0I" 
bot = telebot.TeleBot(BOT_TOKEN)


# =======================================================
# ၃။ BOT အလုပ်လုပ်မည့် စနစ်များ (Commands & Message Handler)
# =======================================================

# /start သို့မဟုတ် /help ဟု ပေးပို့လျှင် တုံ့ပြန်မည့်စနစ်
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎶 မင်္ဂလာပါဗျာ! ကျွန်တော်က သီချင်းဒေါင်းပေးမယ့် Bot ပါ။\n\n"
        "သီချင်းနာမည် (သို့မဟုတ်) YouTube Link ကို ပေးပို့ပြီး "
        "အလွယ်တကူ တောင်းဆိုနိုင်ပါတယ်ဗျာ။"
    )
    bot.reply_to(message, welcome_text)

# အသုံးပြုသူက သီချင်းစာသား ရိုက်ပို့လာလျှင် လုပ်ဆောင်မည့်စနစ်
@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text
    chat_id = message.chat.id
    
    # စတင်ရှာဖွေနေကြောင်း Message အရင်ပြန်ပို့ခြင်း
    status_msg = bot.reply_to(message, "🔍 ယူတုဘတ်မှာ သီချင်းရှာပြီး ဒေါင်းလုဒ်ဆွဲနေပါပြီ၊ ခဏစောင့်ပေးပါဗျာ...")
    
    # yt-dlp အတွက် Audio သီးသန့် MP3 ပြောင်းလဲမည့် စနစ်များ သတ်မှတ်ခြင်း
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'default_search': 'ytsearch1', # စာသားဖြင့် ရှာဖွေလျှင် ပထမဆုံး ဗီဒီယိုကို ယူမည်
        'quiet': True
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # YouTube ဆီကနေ ဒေါင်းလုဒ်ဆွဲခြင်း
            info = ydl.extract_info(query, download=True)
            
            # ရရှိလာတဲ့ ဗီဒီယို အချက်အလက်များကို ယူခြင်း
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            filename = ydl.prepare_filename(video_info)
            # ဒေါင်းပြီးသွားတဲ့ ဖိုင်ကို .mp3 အဖြစ် ပြောင်းလဲသတ်မှတ်ခြင်း
            audio_file = os.path.splitext(filename)[0] + ".mp3"
            
            # ဖိုင် တကယ်ရှိမရှိ စစ်ဆေးပြီး Telegram ဆီ ပို့ပေးခြင်း
            if os.path.exists(audio_file):
                bot.delete_message(chat_id, status_msg.message_id) # ရှာနေဆဲ စာသားကို ဖျက်ပါ
                bot.send_chat_action(chat_id, 'upload_document') # အပေါ်ကနေ ဖိုင်ပို့နေကြောင်း ပြပါ
                
                with open(audio_file, 'rb') as audio:
                    bot.send_audio(chat_id, audio, title=video_info.get('title'))
                
                # ပို့ပြီးသွားလျှင် ဆာဗာထဲက ဖိုင်ကို ပြန်ဖျက်ပြီး နေရာလွတ်ရှင်းလင်းခြင်း
                os.remove(audio_file)
            else:
                bot.edit_message_text("❌ သီချင်းပြောင်းလဲရာတွင် အဆင်မပြေဖြစ်သွားပါသည်၊ ထပ်မံကြိုးစားကြည့်ပါ။", chat_id, status_msg.message_id)
                
    except Exception as e:
        print(f"Error အမှားတက်သွားပါသည်: {e}")
        bot.edit_message_text("❌ ရှာဖွေရယူရာတွင် အဆင်မပြေဖြစ်သွားပါသည်ဗျာ။ အင်တာနက်လိုင်းကြောင့် ဖြစ်နိုင်ပါသည်။", chat_id, status_msg.message_id)

# Bot ကို အမြဲတမ်း ပတ်ထားမည့်စနစ်
print("🚀 Bot စတင်အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
