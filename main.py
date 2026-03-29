import telebot
import os
from telebot import types

# ضع التوكن الخاص بك هنا
API_TOKEN = '8748282530:AAHy0AVK9vbrfLRcJuIJumZtgTsmugo2EPw'
bot = telebot.TeleBot(API_TOKEN)

# مخزن مؤقت لحفظ الروابط لكل مستخدم
user_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 مرحباً بك في بوت التحميل الاحترافي!\n\nأرسل لي رابط الفيديو (يوتيوب أو غيره) وسأعطيك خيارات الجودة المتاحة.")

@bot.message_handler(func=lambda message: "http" in message.text)
def show_options(message):
    url = message.text
    user_data[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # أزرار الفيديو
    v144 = types.InlineKeyboardButton("🎬 فيديو 144p", callback_data="144")
    v360 = types.InlineKeyboardButton("🎬 فيديو 360p", callback_data="360")
    v720 = types.InlineKeyboardButton("🎬 فيديو 720p", callback_data="720")
    v1080 = types.InlineKeyboardButton("🎬 فيديو 1080p", callback_data="1080")
    v4k = types.InlineKeyboardButton("🎬 فيديو 4K (2160p)", callback_data="2160")
    
    # أزرار الصوت بجودات مختلفة
    a_64 = types.InlineKeyboardButton("🎵 صوت MP3 (64k)", callback_data="mp3_64")
    a_128 = types.InlineKeyboardButton("🎵 صوت MP3 (128k)", callback_data="mp3_128")
    a_256 = types.InlineKeyboardButton("🎵 صوت MP3 (256k)", callback_data="mp3_256")
    a_320 = types.InlineKeyboardButton("🎵 صوت MP3 (320k)", callback_data="mp3_320")
    
    # إضافة الأزرار للمجلد
    markup.add(v144, v360, v720, v1080, v4k, a_64, a_128, a_256, a_320)
    
    bot.reply_to(message, "الرجاء اختيار الجودة المطلوبة أو نوع الملف:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def process_download(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    choice = call.data
    
    if not url:
        bot.send_message(chat_id, "❌ انتهت الجلسة، يرجى إرسال الرابط مرة أخرى.")
        return

    bot.edit_message_text("⏳ جاري التحميل والمعالجة.. يرجى الانتظار قليلاً حسب حجم الملف.", chat_id, call.message.message_id)
    
    # تحديد اسم الملف ونوع التحميل
    if "mp3" in choice:
        bitrate = choice.split("_")[1]
        output_file = "audio_download.mp3"
        # أمر تحميل الصوت فقط
        cmd = f'yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k -o "{output_file}" "{url}"'
        is_audio = True
    else:
        output_file = "video_download.mp4"
        # أمر تحميل الفيديو مع دمج الصوت (يحد من الجودة المختارة أو أقل منها)
        cmd = f'yt-dlp -f "bestvideo[height<={choice}]+bestaudio/best" --merge-output-format mp4 -o "{output_file}" "{url}"'
        is_audio = False

    try:
        # تنفيذ الأمر
        os.system(cmd)
        
        if os.path.exists(output_file):
            with open(output_file, 'rb') as f:
                if is_audio:
                    bot.send_audio(chat_id, f, caption="✅ تم تحميل ملف الصوت بنجاح.")
                else:
                    bot.send_video(chat_id, f, caption=f"✅ تم تحميل الفيديو بجودة {choice}p.")
            # حذف الملف بعد الإرسال لتوفير مساحة السيرفر
            os.remove(output_file)
        else:
            bot.send_message(chat_id, "❌ عذراً، فشل التحميل. قد يكون الرابط غير مدعوم أو الجودة غير متوفرة لهذا الفيديو.")
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ حدث خطأ غير متوقع. تأكد أن حجم الملف لا يتجاوز 2 جيجابايت.")

# تشغيل البوت باستمرار
print("Bot is running...")
bot.polling(none_stop=True)
