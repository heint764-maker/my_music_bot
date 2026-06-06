import os
import telebot
import yt_dlp

# ⚠️ Telegram က @BotFather ဆီကရလာတဲ့ Token ကို ဒီနေရာမှာ အစားထိုးထည့်ပါ
BOT_TOKEN = "8946763002:AAGzWsyC6-Gvt_kIgRHmSv8rtAqcXF-pQ0I"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    welcome_text = (
        "🎵 **မြန်မာ Music Downloader Bot မှ ကြိုဆိုပါတယ်!** 🎵\n\n"
        "သင်နားထောင်ချင်တဲ့ သီချင်းနာမည် သို့မဟုတ် YouTube Link ကို ပို့ပေးပါ။ "
        "ကျွန်တော် ရှာဖွေပြီး .mp3 ဖိုင်အဖြစ် ပြန်ပို့ပေးပါမယ်။"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def download_and_send_music(message):
    song_query = message.text
    status_msg = bot.reply_to(message, "🔍 သီချင်းကို YouTube မှာ ရှာဖွေနေပါတယ်... ခေတ္တစောင့်ဆိုင်းပေးပါ။")

    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'outtmpl': '%(title)s.%(ext)s', # ဖိုင်ကို လက်ရှိ folder ထဲပဲ ခေတ္တသိမ်းမယ်
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_query, download=True)
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info
            
            raw_filename = ydl.prepare_filename(video_info)
            filename = os.path.splitext(raw_filename)[0] + ".mp3"
            song_title = video_info.get('title', 'Unknown Song')

        bot.edit_message_text("📤 သီချင်းရပါပြီ! Chat ထဲသို့ ပို့ဆောင်နေပါတယ်...", message.chat.id, status_msg.message_id)
        
        with open(filename, 'rb') as audio_file:
            bot.send_audio(
                chat_id=message.chat.id, 
                audio=audio_file, 
                title=song_title,
                reply_to_message_id=message.message_id
            )
        
        os.remove(filename) # ဖိုင်ပြန်ဖျက်မယ်
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("❌ စိတ်မကောင်းပါဘူး၊ အဲဒီသီချင်းကို ရှာမတွေ့ပါ သို့မဟုတ် ဒေါင်းလုဒ်လုပ်ရတာ အဆင်မပြေဖြစ်သွားပါတယ်။", message.chat.id, status_msg.message_id)

print("🚀 Bot စတင်အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
