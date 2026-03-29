import telebot
import os
from telebot import types

# التوكن الخاص بك
API_TOKEN = '8748282530:AAHy0AVK9vbrfLRcJuIJumZtgTsmugo2EPw'
bot = telebot.TeleBot(API_TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 أهلاً بك! أرسل رابط الفيديو للتحميل.")

@bot.message_handler(func=lambda message: "http" in message.text)
def show_options(message):
    url = message.text
    user_data[message.chat.id] = url
    markup = types.InlineKeyboardMarkup(row_width=2)
    v_btns = [types.InlineKeyboardButton(f"🎬 {res}p", callback_data=res) for res in ["360", "720", "1080"]]
    a_btn = types.InlineKeyboardButton("🎵 MP3 (عالي)", callback_data="mp3_128")
    markup.add(*v_btns, a_btn)
    bot.reply_to(message, "اختر الجودة المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def process_download(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    choice = call.data
    bot.edit_message_text("⏳ جاري المعالجة.. يرجى الانتظار.", chat_id, call.message.message_id)
    
    output = "file.mp3" if "mp3" in choice else "file.mp4"
    
    # الكود المطور لتجاوز الحظر
    if "mp3" in choice:
        cmd = f'yt-dlp --no-check-certificate -x --audio-format mp3 -o "{output}" "{url}"'
    else:
        cmd = f'yt-dlp --no-check-certificate -f "bestvideo[height<={choice}]+bestaudio/best" --merge-output-format mp4 -o "{output}" "{url}"'

    try:
        os.system(cmd)
        if os.path.exists(output):
            with open(output, 'rb') as f:
                if "mp3" in choice:
                    bot.send_audio(chat_id, f, caption="تم تحميل الصوت بنجاح 🎶")
                else:
                    bot.send_video(chat_id, f, caption=f"تم التحميل بجودة {choice}p ✅")
            os.remove(output)
        else:
            bot.send_message(chat_id, "❌ فشل التحميل. يوتيوب قد يطلب ملف Cookies.")
    except Exception as e:
        bot.send_message(chat_id, "⚠️ حدث خطأ في الإرسال.")

bot.polling(none_stop=True)

