import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp

# Loglama ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 **@OnsraMusicBot Müzik Botuna Hoş Geldiniz!**\n\n"
        "• Bana bir **şarkı adı** yazabilirsiniz, size arama sonuçlarını liste olarak sunarım.\n"
        "• Veya doğrudan bir **şarkı linki** atabilirsiniz, hemen MP3 olarak indirip gönderirim."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.startswith("http://") or text.startswith("https://"):
        await update.message.reply_text("⏳ Link işleniyor, lütfen bekleyin...")
        try:
            mp3_file = download_audio(text)
            if mp3_file and os.path.exists(mp3_file):
                await update.message.reply_audio(audio=open(mp3_file, 'rb'))
                os.remove(mp3_file)
            else:
                await update.message.reply_text("❌ Şarkı indirilemedi.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Bir hata oluştu: {str(e)}")
    else:
        await update.message.reply_text("🔍 Şarkı aranıyor...")
        try:
            results = search_youtube(text, limit=5)
            if not results:
                await update.message.reply_text("❌ Hiçbir sonuç bulunamadı.")
                return

            keyboard = []
            for item in results:
                keyboard.append([InlineKeyboardButton(item['title'], callback_data=f"dl_{item['id']}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🎧 İndirmek istediğiniz şarkıyı seçin:", reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Arama sırasında hata oluştu: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("dl_"):
        video_id = data.split("_")[1]
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        await query.edit_message_text(text="⏳ Seçilen şarkı indiriliyor, gönderiliyor...")
        try:
            mp3_file = download_audio(url)
            if mp3_file and os.path.exists(mp3_file):
                await query.message.reply_audio(audio=open(mp3_file, 'rb'))
                os.remove(mp3_file)
            else:
                await query.message.reply_text("❌ Şarkı indirilemedi.")
        except Exception as e:
            await query.message.reply_text(f"⚠️ İndirme hatası: {str(e)}")

def search_youtube(query, limit=5):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        results = []
        if 'entries' in info:
            for entry in info['entries']:
                results.append({
                    'id': entry.get('id'),
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
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, ext = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        return mp3_filename

if __name__ == '__main__':
    TOKEN = "8222625062:AAH-GZ2GCLNcQE0YS_fAQekyBgDuiGxv0p8"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot çalışıyor...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def main():
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
            if mp3_file and os.path.exists(mp3_file):
                await query.message.reply_audio(audio=open(mp3_file, 'rb'))
                os.remove(mp3_file)
            else:
                await query.message.reply_text("❌ Şarkı indirilemedi.")
        except Exception as e:
            await query.message.reply_text(f"⚠️ İndirme hatası: {str(e)}")

def search_youtube(query, limit=5):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        results = []
        if 'entries' in info:
            for entry in info['entries']:
                results.append({
                    'id': entry.get('id'),
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
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, ext = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        return mp3_filename

if __name__ == '__main__':
    TOKEN = "import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp

# Loglama ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 **@OnsraMusicBot Müzik Botuna Hoş Geldiniz!**\n\n"
        "• Bana bir **şarkı adı** yazabilirsiniz, size arama sonuçlarını liste olarak sunarım.\n"
        "• Veya doğrudan bir **şarkı linki** atabilirsiniz, hemen MP3 olarak indirip gönderirim."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.startswith("http://") or text.startswith("https://"):
        await update.message.reply_text("⏳ Link işleniyor, lütfen bekleyin...")
        try:
            mp3_file = download_audio(text)
            if mp3_file and os.path.exists(mp3_file):
                await update.message.reply_audio(audio=open(mp3_file, 'rb'))
                os.remove(mp3_file)
            else:
                await update.message.reply_text("❌ Şarkı indirilemedi.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Bir hata oluştu: {str(e)}")
    else:
        await update.message.reply_text("🔍 Şarkı aranıyor...")
        try:
            results = search_youtube(text, limit=5)
            if not results:
                await update.message.reply_text("❌ Hiçbir sonuç bulunamadı.")
                return

            keyboard = []
            for item in results:
                keyboard.append([InlineKeyboardButton(item['title'], callback_data=f"dl_{item['id']}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🎧 İndirmek istediğiniz şarkıyı seçin:", reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Arama sırasında hata oluştu: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("dl_"):
        video_id = data.split("_")[1]
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        await query.edit_message_text(text="⏳ Seçilen şarkı indiriliyor, gönderiliyor...")
        try:
            mp3_file = download_audio(url)
            if mp3_file and os.path.exists(mp3_file):
                await query.message.reply_audio(audio=open(mp3_file, 'rb'))
                os.remove(mp3_file)
            else:
                await query.message.reply_text("❌ Şarkı indirilemedi.")
        except Exception as e:
            await query.message.reply_text(f"⚠️ İndirme hatası: {str(e)}")

def search_youtube(query, limit=5):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        results = []
        if 'entries' in info:
            for entry in info['entries']:
                results.append({
                    'id': entry.get('id'),
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
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, ext = os.path.splitext(filename)
        mp3_filename = base + ".mp3"
        return mp3_filename

if __name__ == '__main__':
    TOKEN = "BURAYA_BOT_TOKEN_GIRIN"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot çalışıyor...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def main():
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
        "
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot çalışıyor...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def main():
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
