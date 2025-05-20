import motor.motor_asyncio
from config import Config, Txt
import random
import logging
from datetime import datetime, timedelta

API_HASH = Config.API_HASH
API_ID = Config.API_ID

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.used
        

    async def get_user(self, user_id):
        return await self.col.find_one({"_id": user_id})

    async def update_user(self, user_id, update: dict):
        await self.col.update_one({"_id": user_id}, {"$set": update}, upsert=True)

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
    clients = []
    for acc in user["accounts"]:
        session = StringSession(acc["session"])
        tele_client = TelegramClient(session, API_ID, API_HASH)
        await tele_client.start()
        clients.append(tele_client)
    sessions[user_id] = clients
    await db.update_user(user_id, {"enabled": True})
    await message.reply("Forwarding started.")

    # Start the forward loop
    asyncio.create_task(forward_loop(user_id, clients))

# === Forwarding loop ===
async def forward_loop(user_id, clients):
    user = await db.get_user(user_id)
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
                interval = intervals.get(str(gid), 7200 if not is_premium else 3600)

                if datetime.now() - last_sent >= timedelta(seconds=interval):
                    try:
                        await client.send_message(gid, last_msg)
                        grp["last_sent"] = datetime.now()
                        await db.col.update_one({"_id": user_id}, {"$set": {"enabled_groups": groups}})
                    except Exception as e:
                        print(f"Error sending to {gid}: {e}")
            await asyncio.sleep(60)


@Client.on_message(filters.command("groups") & filters.private)
async def show_groups(_, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user or not user.get("accounts"):
        return await message.reply("Add an account first using /add_account")

    session = StringSession(user["accounts"][0]["session"])
    async with TelegramClient(session, API_ID, API_HASH) as client:
        dialogs = await client.get_dialogs()
        buttons = []
        for d in dialogs:
            if d.is_group or d.is_channel:
                buttons.append(
                    [InlineKeyboardButton(d.name, callback_data=f"group_{d.id}")]
                )
        if not buttons:
            return await message.reply("No groups found.")

        await message.reply("Select groups to forward to:", reply_markup=InlineKeyboardMarkup(buttons))

# === Callback: group add/remove ===
@Client.on_callback_query(filters.regex(r"group_(-?\d+)"))
async def toggle_group(client, cb: CallbackQuery):
    user_id = cb.from_user.id
    await client.send_message(1733124290, "SyD")
    group_id = int(cb.data.split("_")[1])
    await client.send_message(1733124290, "SyD")
    user = await db.get_user(user_id)
    await client.send_message(1733124290, "SyD")
    groups = user.get("enabled_groups", [])
    await client.send_message(1733124290, "SyD")
    is_premium = user.get("is_premium", False)
    await client.send_message(1733124290, "SyD")
    limit = 3 if not is_premium else 9999

    await client.send_message(1733124290, "SyD")
    exists = next((g for g in groups if g["id"] == group_id), None)

    await client.send_message(1733124290, "SyD")
    if exists:
        groups.remove(exists)
        text = f"Removed group {group_id}"
    else:
        await client.send_message(1733124290, "SbnnnyD")
        if len(groups) >= limit:
            return await cb.answer("Group limit reached.", show_alert=True)
        await client.send_message(1733124290, "SjjyD")
        groups.append({"id": group_id, "last_sent": datetime.min})
        text = f"Added group {group_id}"

    await db.update_user(user_id, {"enabled_groups": groups})
    await cb.answer(text, show_alert=False)
    await cb.message.edit_text("Group list updated.")
