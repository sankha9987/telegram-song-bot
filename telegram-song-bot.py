import os
import random
import asyncio
from datetime import datetime
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Store user search history
user_searches = {}

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

# === /start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first = update.effective_user.first_name
    message = (
        f"👋 Hello {user_first}!\n\n"
        "I'm your friendly song bot. Here's what I can do:\n"
        "🎵 /song <name> — Download a song from YouTube.\n"
        "🧹 /clear — I'll delete your recent messages.\n\n"
        "Enjoy the vibes! 🎧"
    )
    await update.message.reply_text(message)

# === /song Command ===
async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /song <song name>")
        return

    query = " ".join(context.args)
    user_id = update.effective_user.id
    user_first = update.effective_user.first_name

    # Save to user history
    user_searches.setdefault(user_id, []).append(query)

    await update.message.reply_text(f"🎵 Searching for: {query} , Please wait few seconds ...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = info.get("title", "audio")

        if not os.path.exists(filename):
            await update.message.reply_text("⚠ Couldn't find the song file after downloading.")
            return

        await update.message.reply_audio(audio=open(filename, 'rb'), title=title)

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("❌ Failed to find or send the song. Please try another name.")

# === /clear Command ===
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id

    async for msg in chat.get_history(limit=50):
        if msg.from_user.id == user_id:
            try:
                await msg.delete()
            except:
                pass
    await update.message.reply_text("🧹 Chat cleared (as much as I can).")

# === Scheduled Task ===
async def send_periodic_song(app):
    while True:
        await asyncio.sleep(4 * 60 * 60)  # 4 hours
        for user_id, searches in user_searches.items():
            if searches:
                query = random.choice(searches)
                try:
                    chat = await app.bot.get_chat(user_id)
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': 'downloads/%(title)s.%(ext)s',
                        'noplaylist': True,
                        'quiet': True,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }

                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
                        title = info.get("title", "audio")

                    if os.path.exists(filename):
                        await chat.send_message(f"Hello {chat.first_name}, feeling bored?\nHere's something to make you happy 🎶")
                        await chat.send_audio(audio=open(filename, 'rb'), title=title)

                except Exception as e:
                    print(f"Error sending periodic song to {user_id}:", e)

# === Main ===
async def main():
    app = ApplicationBuilder().token("7550948741:AAF3hflHHQKBKjuAT0MX6Ux9XbRDn_ER3NU").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", song))
    app.add_handler(CommandHandler("clear", clear))
    print("🤖 Bot is running...")

    # Start background task
    asyncio.create_task(send_periodic_song(app))

    await app.run_polling()

# === Entry Point ===
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
