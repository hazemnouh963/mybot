import telebot
import os
from telebot import types

API_TOKEN = '8748282530:AAG7CA64wrNvvac5C0szv4cFghQMHZ8awgc' 
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ البوت شغال! أرسل الرابط الآن.")

@bot.message_handler(func=lambda m: "http" in m.text)
def get_url(message):
    url = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تحميل MP4", callback_data=f"vid_{url}"))
    bot.reply_to(message, "اختر النوع:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def download(call):
    url = call.data.split("vid_")[1]
    bot.edit_message_text("⏳ جاري التحميل...", call.message.chat.id, call.message.message_id)
    os.system(f'yt-dlp --no-check-certificate -f "best" -o "video.mp4" "{url}"')
    if os.path.exists("video.mp4"):
        with open("video.mp4", 'rb') as f:
            bot.send_video(call.message.chat.id, f)
        os.remove("video.mp4")
    else:
        bot.send_message(call.message.chat.id, "❌ فشل، جرب رابط آخر.")

bot.polling(none_stop=True)
