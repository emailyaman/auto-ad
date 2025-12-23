from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from aiohttp import web

api_id = 27502961
api_hash = "b8d9acdc18d1352241239aab9e348fa5"
SESSION = "1BVtsOGoBu4YjwHkBYKqTHv7UKFzNIeBH4e74jBnffrlufrN9oQdjza1Kvp4pLUG4RYK6BjCosbhqaF46kZ2IwyMRYw3YrrsU3vjFA6fYaipX2QajhqVhj7QO9NDIQjz1pKNvMkHeyllVpf1c9CDu4OHNgbl4gpFq2LRNi9POO4SUppfyij3b3wmR468f5omzzRFqAwAl56b6W8m-aipIkW0nK1zvGLFdKgJnV6Bv7j19umIlVunkbfHp8N9Mt7P7u63K25ufwB2_0gPSOXe4dff-pmkElkdEYoNhqVzg9q5VURWNjWAEoLrajDewn0x2XabJHTjurz49Jxjln4B2PWdsmXldFNY="

client = TelegramClient(StringSession(SESSION), api_id, api_hash)

spam_tasks = {}

@client.on(events.NewMessage(pattern=r"\.dspam (\d+) (.+)"))
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

async def main():
    await client.start()
    print("Bot is running...")
    await client.run_until_disconnected()

asyncio.run(main())
