import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp

# Loglama ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Arama sonuçlarını geçici olarak saklamak için sözlük
search_cache = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 **@OnsraMusicBot Müzik Botuna Hoş Geldiniz!**\n\n"
        "• Bana bir **şarkı veya sanatçı adı** yazabilirsiniz, size SoundCloud üzerinden arama sonuçlarını sunarım.\n"
        "• Veya doğrudan bir **SoundCloud / YouTube linki** atabilirsiniz, hemen MP3 olarak indirip gönderirim."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.message.from_user.id

    if text.startswith("http://") or text.startswith("https://"):
        await update.message.reply_text("⏳ Link işleniyor, lütfen bekleyin...")
        try:
            mp3_file, title, uploader = download_audio(text)
            if mp3_file and os.path.exists(mp3_file):
                await update.message.reply_audio(
                    audio=open(mp3_file, 'rb'),
                    title=title,
                    performer=uploader
                )
                os.remove(mp3_file)
            else:
                await update.message.reply_text("❌ Şarkı indirilemedi.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Bir hata oluştu: {str(e)}")
    else:
        await update.message.reply_text("🔍 SoundCloud üzerinde aranıyor...")
        try:
            results = search_soundcloud(text, limit=5)
            if not results:
                await update.message.reply_text("❌ Hiçbir sonuç bulunamadı.")
                return

            search_cache[user_id] = results

            keyboard = []
            for index, item in enumerate(results):
                keyboard.append([InlineKeyboardButton(item['title'], callback_data=f"dl_{index}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🎧 İndirmek istediğiniz şarkıyı seçin:", reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Arama sırasında hata oluştu: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id

    if not data.startswith("dl_"):
        await query.edit_message_text(text="❌ Bu menü geçerliliğini yitirmiş. Lütfen yeniden şarkı adı yazarak arama yapın.")
        return

    try:
        parts = data.split("_")
        if len(parts) < 2:
            await query.edit_message_text(text="❌ Geçersiz seçim. Lütfen tekrar arama yapın.")
            return
            
        index = int(parts[1])
        
        if user_id not in search_cache or index >= len(search_cache[user_id]):
            await query.edit_message_text(text="❌ Zaman aşımı veya eski liste. Lütfen tekrar arama yapın.")
            return

        url = search_cache[user_id][index]['url']
        
        await query.edit_message_text(text="⏳ Seçilen şarkı indiriliyor, gönderiliyor...")
        
        mp3_file, title, uploader = download_audio(url)
        if mp3_file and os.path.exists(mp3_file):
            await query.message.reply_audio(
                audio=open(mp3_file, 'rb'),
                title=title,
                performer=uploader
            )
            os.remove(mp3_file)
        else:
            await update.message.reply_text("❌ Şarkı indirilemedi.")
    except Exception as e:
        await query.message.reply_text(f"⚠️ İndirme hatası: {str(e)}")

def search_soundcloud(query, limit=5):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"scsearch{limit}:{query}", download=False)
        results = []
        if 'entries' in info:
            for entry in info['entries']:
                results.append({
                    'url': entry.get('url'),
                    'title': entry.get('title')
                })
        return results

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, ext = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        
        title = info.get('title', 'Bilinmeyen Şarkı')
        uploader = info.get('uploader', 'Bilinmeyen Sanatçı')
        
        return mp3_filename, title, uploader

def main():
    TOKEN = "8222625062:AAFHBf5VPh_kSdSgFO3iuXDA4dteyYFDWyA"
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot başlatıldı, mesajlar dinleniyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
