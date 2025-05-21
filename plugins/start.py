import motor.motor_asyncio
from config import Config, Txt
import random
import logging
from datetime import datetime, timedelta
sessions = {}
API_HASH = Config.API_HASH
API_ID = Config.API_ID

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.used
        self.group = self.db.groups  # <- new group collection for session-user group storage

        

    async def get_user(self, user_id):
        return await self.col.find_one({"_id": user_id})

    async def update_user(self, user_id, update: dict):
        await self.col.update_one({"_id": user_id}, {"$set": update}, upsert=True)

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

db = Database(Config.DB_URL, Config.DB_NAME)

logger = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):

    if message.from_user.id in Config.BANNED_USERS:
        await message.reply_text("Sorry, You are banned.")
        return

    user = message.from_user
    await db.add_user(client, message)
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '⛅ Uᴘᴅᴀᴛᴇꜱ', url=f'https://t.me/{Config.UPDATES}'),
        InlineKeyboardButton(
            ' Sᴜᴘᴘᴏʀᴛ 🌨️', url=f'https://t.me/{Config.SUPPORT}')
    ], [
        InlineKeyboardButton('❄️ Δʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton(' Hᴇʟᴩ ❗', callback_data='help')
    ], [InlineKeyboardButton('⚙️ sᴛΔᴛs ⚙️', callback_data='stats')]])
    if Config.PICS:
        await message.reply_photo(random.choice(Config.PICS), caption=Txt.START_TXT.format(user.mention), reply_markup=button, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)




@Client.on_message(filters.command("run") & filters.private)
async def run_forwarding(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user or not user.get("accounts"):
        return await message.reply("No userbot account found. Use /add_account first.")

    if not user.get("enabled_groups"):
        return await message.reply("No groups selected. Use /groups to add some.")

    # Start sessions
    await message.reply("check")
    clients = []
    for acc in user["accounts"]:
        await message.reply("check")
        session = StringSession(acc["session"])
        await message.reply("check")
        tele_client = TelegramClient(session, Config.API_ID, Config.API_HASH)
        await tele_client.start()
        await message.reply("check")
        clients.append(tele_client)
    await message.reply("check")
    sessions[user_id] = clients
    await db.update_user(user_id, {"enabled": True})
    await message.reply("Forwarding started.")
    groups = user.get("enabled_groups", [])
    is_premium = user.get("is_premium", False)
    intervals = user.get("intervals", {})

    for i, client in enumerate(clients):
        if i > 0:
            await asyncio.sleep(600)  # 10 minutes delay per extra userbot

        while True:
            if not (await db.get_user(user_id)).get("enabled", False):
                break  # stop if disabled

            last_msg = (await client.get_messages("me", limit=1))[0]
            for grp in groups:
                gid = grp["id"]
                last_sent = grp.get("last_sent", datetime.min)
                interval = intervals.get(str(gid), 7 if not is_premium else 3)

                if datetime.now() - last_sent >= timedelta(seconds=interval):
                    try:
                        await client.send_message(gid, last_msg)
                        grp["last_sent"] = datetime.now()
                        await db.col.update_one({"_id": user_id}, {"$set": {"enabled_groups": groups}})
                    except Exception as e:
                        print(f"Error sending to {gid}: {e}")
            await asyncio.sleep(60)



@Client.on_message(filters.command("groups") & filters.private)
async def show_accounts(client: Client, message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user or not user.get("accounts"):
        return await message.reply("Please add an account first using /add_account")

    accounts = user["accounts"]
    buttons = []

    # Load names from each session
    for i, acc in enumerate(accounts):
        try:
            async with TelegramClient(StringSession(acc["session"]), Config.API_ID, Config.API_HASH) as userbot:
                me = await userbot.get_me()
                acc_name = me.first_name or me.username or f"Account {i+1}"
        except Exception:
            acc_name = f"Account {i+1} (invalid)"
        
        buttons.append([
            InlineKeyboardButton(acc_name, callback_data=f"choose_account_{i}")
        ])

    await message.reply(
        "Choose an account to manage groups:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

