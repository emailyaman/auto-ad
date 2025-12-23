from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from aiohttp import web

api_id = 123456
api_hash = "YOUR_API_HASH"
SESSION = "YOUR_SESSION_STRING_HERE"

client = TelegramClient(StringSession(SESSION), api_id, api_hash)

spam_tasks = {}

@client.on(events.NewMessage(pattern=r"\.dspam (\d+) ([\s\S]+)"))
async def start_spam(event):
    chat_id = event.chat_id
    
    if chat_id in spam_tasks:
        await event.reply("⚠️ Already spamming here. Use .dstop.")
        return
    
    minutes = int(event.pattern_match.group(1))
    message = event.pattern_match.group(2)
    
    chat = await event.get_chat()
    
    async def spam_loop():
        while True:
            try:
                await client.send_message(chat, message)
                await asyncio.sleep(minutes * 60)
            except Exception as e:
                print(f"Error: {e}")
                break
    
    spam_tasks[chat_id] = asyncio.create_task(spam_loop())
    await event.reply(f"✅ Sending every {minutes} minutes in this chat.")

@client.on(events.NewMessage(pattern=r"\.dstop"))
async def stop_spam(event):
    chat_id = event.chat_id
    task = spam_tasks.pop(chat_id, None)
    if task:
        task.cancel()
        await event.reply("🛑 Stopped spamming in this chat.")
    else:
        await event.reply("ℹ️ No active spam task here.")

async def health_check(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("HTTP server started on port 8080")

async def main():
    print("Starting HTTP server...")
    await start_web_server()
    
    print("Starting Telegram bot...")
    try:
        await client.start()
        print("Bot connected successfully!")
    except Exception as e:
        print(f"Error connecting to Telegram: {e}")
    
    await client.run_until_disconnected()

asyncio.run(main())
