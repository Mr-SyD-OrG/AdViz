from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod.exceptions import ListenerTimeout
from config import Txt, Config
from .start import db
from telethon import TelegramClient
from telethon.sessions import StringSession


@Client.on_message(filters.command("upgrade") & filters.user(Config.ADMIN))  # Replace with your admin ID
async def upgrade_user(client: Client, message: Message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Usage: /upgrade <user_id>")
    
    target_id = int(parts[1])
    await db.update_user(target_id, {"is_premium": True})
    await message.reply(f"User `{target_id}` has been upgraded to Premium.")




@Client.on_message(filters.command("add_account") & filters.private)
async def add_account_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user and not user.get("is_premium", False) and len(user.get("accounts", [])) >= 1:
        return await message.reply("Free users can only add one account. Upgrade to premium for more.")

    try:
        metadata = await bot.ask(
            text="Please send your **Telethon StringSession**.\n\nTimeout in 30 seconds.",
            chat_id=user_id,
            filters=filters.text,
            timeout=30,
            disable_web_page_preview=True
        )
    except ListenerTimeout:
        return await message.reply_text(
            "⚠️ Error!!\n\n**Request timed out.**\nRestart by using /add_account",
            reply_to_message_id=message.id
        )

    string = metadata.text.strip()

    # Try initializing to validate the session
    try:
        async with TelegramClient(StringSession(string), Config.API_ID, Config.API_HASH) as userbot:
            await userbot.get_me()
    except Exception as e:
        return await message.reply(f"Invalid session string.\n\nError: `{e}`")

    # Save to DB
    if not user:
        user = {"_id": user_id, "accounts": []}

    user.setdefault("accounts", []).append({"session": string})
    await db.update_user(user_id, user)
    await message.reply("Account added successfully and validated.")
