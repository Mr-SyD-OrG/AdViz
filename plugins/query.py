import shutil
import time
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from config import Config, Txt
from .start import db
import random
from telethon.tl.functions.messages import GetForumTopicsRequest
import psutil
from helper.utils import humanbytes
from telethon.sessions import StringSession
from telethon import TelegramClient
from datetime import datetime



async def toggle_group_directly(tg_client, user, group_id, session_user_id, query, account_index):
    from datetime import datetime

    group_data = await db.group.find_one({"_id": session_user_id}) or {"_id": session_user_id, "groups": []}
    group_list = group_data["groups"]

    exists = next((g for g in group_list if g["id"] == group_id), None)

    if exists:
        group_list.remove(exists)
        status = "❌"
        message = "Group removed"
    else:
        is_premium = user.get("is_premium", False)
        limit = 3 if not is_premium else 1000
        if len(group_list) >= limit:
            return await query.answer("Group limit reached.", show_alert=True)
        group_list.append({"id": group_id, "last_sent": datetime.min})
        status = "✅"
        message = "Group added"

    await db.group.update_one({"_id": session_user_id}, {"$set": {"groups": group_list}}, upsert=True)
    await query.answer(message + " " + status, show_alert=False)
    await query.message.delete()
    await show_groups_for_account(tg_client, query.message, query.from_user.id, account_index)

async def show_groups_for_account(client, message, user_id, account_index):
    user = await db.get_user(user_id)
    await client.send_message(1733124290, "SyD")
    session_str = user["accounts"][account_index]["session"]
    await client.send_message(1733124290, "SyD")
    async with TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH) as tg_client:
        me = await tg_client.get_me()
        await client.send_message(1733124290, "SyD")
        session_user_id = me.id

        await client.send_message(1733124290, "SyD")
        group_data = await db.group.find_one({"_id": session_user_id}) or {}
        await client.send_message(1733124290, "SyD")
        enabled_ids = {g["id"] for g in group_data.get("groups", [])}

        await client.send_message(1733124290, "SyD")

        dialogs = await tg_client.get_dialogs()
        await client.send_message(1733124290, "SyD")
        buttons = []

        for d in dialogs:
            if d.is_group or d.is_channel:
                is_enabled = "✅" if d.id in enabled_ids else "❌"
                title = f"{d.name} {is_enabled}"
                buttons.append([
                    InlineKeyboardButton(title, callback_data=f"group_{d.id}_{account_index}")
                ])

        buttons.append([InlineKeyboardButton("◀️ Go Back", callback_data="back_to_accounts")])
        await message.reply("Select groups to forward to:", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
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
        user = await db.get_user(query.from_user.id)
        accounts = user.get("accounts", [])
        buttons = []

        for i, acc in enumerate(accounts):
            try:
                async with TelegramClient(StringSession(acc["session"]), Config.API_ID, Config.API_HASH) as userbot:
                    me = await userbot.get_me()
                    acc_name = me.first_name or me.username or f"Account {i+1}"
            except Exception:
                acc_name = f"Account {i+1} (invalid)"

            buttons.append([InlineKeyboardButton(acc_name, callback_data=f"choose_account_{i}")])

        await query.message.edit_text(
            "Choose an account:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # === Group Selection ===
        elif data.startswith("group_"):
        parts = data.split("_")
        group_id = int(parts[1])
        account_index = int(parts[2])

        user = await db.get_user(query.from_user.id)
        session_str = user["accounts"][account_index]["session"]

        async with TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH) as tg_client:
            me = await tg_client.get_me()
            session_user_id = me.id

            entity = await tg_client.get_entity(group_id)

            # If group does not have forum (topic) enabled
            if not getattr(entity, "forum", False):
                await toggle_group_directly(tg_client, user, group_id, session_user_id, query, account_index)
            else:
                try:
                    topics = await tg_client(GetForumTopicsRequest(
                        channel=entity,
                        offset_date=0,
                        offset_id=0,
                        offset_topic=0,
                        limit=100
                    ))

                    topic_buttons = []
                    for topic in topics.topics:
                        topic_buttons.append([
                            InlineKeyboardButton(
                                topic.title,
                                callback_data=f"topic_{group_id}_{account_index}_{topic.id}"
                            )
                        ])
                    topic_buttons.append([
                        InlineKeyboardButton("◀️ Go Back", callback_data=f"back_groups_{account_index}")
                    ])
                    await query.message.edit_text("Select a topic:", reply_markup=InlineKeyboardMarkup(topic_buttons))

                except Exception as e:
                    print(f"Failed to fetch topics: {e}")
                    await query.answer("Failed to fetch topics.", show_alert=True)


    elif data.startswith("topic_"):
        parts = data.split("_")
        group_id = int(parts[1])
        account_index = int(parts[2])
        topic_id = int(parts[3])

        user = await db.get_user(query.from_user.id)
        session_str = user["accounts"][account_index]["session"]

        async with TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH) as tg_client:
            me = await tg_client.get_me()
            session_user_id = me.id

            group_data = await db.group.find_one({"_id": session_user_id}) or {"_id": session_user_id, "groups": []}
            group_list = group_data["groups"]

            # Avoid duplicate
            exists = next((g for g in group_list if g["id"] == group_id and g.get("topic_id") == topic_id), None)
            if not exists:
                group_list.append({"id": group_id, "topic_id": topic_id, "last_sent": datetime.min})
                await db.group.update_one({"_id": session_user_id}, {"$set": {"groups": group_list}}, upsert=True)
                await query.answer("Group with topic added ✅", show_alert=False)
            else:
                await query.answer("Already added", show_alert=True)

        await query.message.delete()
        await show_groups_for_account(client, query.message, query.from_user.id, account_index)

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

    elif data.startswith("choose_delete_"):
        index = int(data.split("_")[-1])
        user_id = query.from_user.id
        user = await db.get_user(user_id)

        if not user or index >= len(user.get("accounts", [])):
            return await query.answer("Invalid selection.", show_alert=True)
        
        try:
            async with TelegramClient(StringSession(account["session"]), Config.API_ID, Config.API_HASH) as tg_client:
                me = await tg_client.get_me()
                await db.group.delete_one({"_id": me.id})
        except:
            pass
        account = user["accounts"].pop(index)
        await db.col.update_one({"_id": user_id}, {"$set": {"accounts": user["accounts"]}})
        await query.edit_message_text("Account and its groups have been deleted.")


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
