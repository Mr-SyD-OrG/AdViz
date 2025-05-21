import shutil
import time
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from config import Config, Txt
from .start import db
import random
import psutil
from info import AUTH_CHANNEL
from helper.utils import humanbytes
from telethon.sessions import StringSession
from telethon import TelegramClient
from datetime import datetime


    
async def show_groups_for_account(client, message, user_id, account_index):
    user = await db.get_user(user_id)
    session_str = user["accounts"][account_index]["session"]

    async with TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH) as tg_client:
        me = await tg_client.get_me()
        session_user_id = me.id

        group_data = await db.usr.find_one({"_id": session_user_id}) or {}
        enabled_ids = {g["id"] for g in group_data.get("groups", [])}

        dialogs = await tg_client.get_dialogs()
        buttons = []

        for d in dialogs:
            if d.is_group or d.is_channel:
                is_enabled = "✅" if d.id in enabled_ids else "❌"
                title = f"{is_enabled} {d.name}"
                buttons.append([
                    InlineKeyboardButton(title, callback_data=f"group_{d.id}_{account_index}")
                ])

        buttons.append([InlineKeyboardButton("◀️ Go Back", callback_data="back_to_accounts")])
        await message.reply("Select groups to forward to:", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    if data == "start":
        await query.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.PICS),
                Txt.START_TXT.format(query.from_user.mention),

            ),

            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    '⛅ Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/{Config.UPDATES}'),
                InlineKeyboardButton(
                    'Sᴜᴩᴩᴏʀᴛ ⛈️', url='https://t.me/{Config.SUPPORT}')
            ], [
                InlineKeyboardButton('❄️ Δʙᴏᴜᴛ', callback_data='about'),
                InlineKeyboardButton('Hᴇʟᴩ ❗', callback_data='help')
            ]])
        )

    elif data.startswith("choose_account_"):
        index = int(data.split("_")[-1])
        await query.message.delete()
        await show_groups_for_account(client, query.message, user_id, index)

    # === Go Back ===
    elif data == "back_to_accounts":
        accounts = user.get("accounts", [])
        buttons = [
            [InlineKeyboardButton(f"Account {i+1}", callback_data=f"choose_account_{i}")]
            for i in range(len(accounts))
        ]
        return await query.message.edit_text("Choose an account:", reply_markup=InlineKeyboardMarkup(buttons))

    # === Group Selection ===
    elif data.startswith("group_"):
        try:
            group_id, acc_index = map(int, data.split("_")[1:])
        except:
            return await query.answer("Invalid data", show_alert=True)

        session_str = user["accounts"][acc_index]["session"]

        # Get the userbot's own user ID (session user ID)
        async with TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH) as userbot:
            me = await userbot.get_me()
            session_user_id = me.id

        # Use session_user_id to load/store group selections
        group_data = await db.usr.find_one({"_id": session_user_id}) or {"_id": session_user_id, "groups": []}
        group_list = group_data.get("groups", [])

        exists = next((g for g in group_list if g["id"] == group_id), None)
        is_premium = user.get("is_premium", False)
        limit = 3 if not is_premium else 9999

        if exists:
            group_list.remove(exists)
        else:
            if len(group_list) >= limit:
                return await query.answer("⚠️ Group limit reached.", show_alert=True)
            group_list.append({"id": group_id, "last_sent": datetime.min})

        # Update DB
        await db.usr.update_one(
            {"_id": session_user_id},
            {"$set": {"groups": group_list}},
            upsert=True
        )

        await show_groups_for_account(client, query.message, user_id, acc_index)

    elif data == "help":

        await query.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.PICS),
                Txt.HELP_TXT

            ),

            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("ᐊ ʙᴀᴄᴋ", callback_data="start"),
                InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close")
                
            ]])
        )

   

    elif data == "about":
        await query.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.PICS),
                Txt.ABOUT_TXT.format(client.mention),

            ),

            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("ᐊ ʙᴀᴄᴋ", callback_data="start"),
                InlineKeyboardButton("✘ ᴄʟᴏsᴇ", callback_data="close")
                
            ]])
        )

    elif data == 'stats':
        buttons = [[InlineKeyboardButton(
            '• ʙᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('⟲ ʀᴇʟᴏᴀᴅ', callback_data='stats')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(
            time.time() - Config.BOT_UPTIME))
        total, used, free = shutil.disk_usage(".")
        total = humanbytes(total)
        used = humanbytes(used)
        free = humanbytes(free)
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        await query.message.edit_media(
            InputMediaPhoto(
                random.choice(Config.PICS),
                Txt.STATS_TXT.format(
                    currentTime, total, used, disk_usage, free, cpu_usage, ram_usage)
            ),
            reply_markup=reply_markup
        )

    
    elif data.startswith("grop_"):
        group_id = int(data.split("_", 1)[1])
        user = await db.get_user(query.from_user.id)
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

        await db.update_user(query.from_user.id, {"enabled_groups": groups})
        await query.answer(text, show_alert=False)
        await query.message.edit_text("Group list updated.")

        #await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('❌ ʀᴇᴍᴏᴠᴇ ❌', callback_data='rmuserbot')], [InlineKeyboardButton('✘ ᴄʟᴏsᴇ ✘', callback_data='close')]]))

    elif data == 'rmuserbot':
        try:
            await db.remove_user_bot(query.from_user.id)
            await query.message.edit(text='**User Bot Removed Successfully ✅**', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('✘ ᴄʟᴏsᴇ ✘', callback_data='close')]]))
        except:
            await query.answer(f'Hey {query.from_user.first_name}\n\n You have already deleted the user')

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()
