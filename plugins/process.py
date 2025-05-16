import random
import logging
import asyncio
import os, re
import time
from time import sleep
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, ForceReply
from pyrogram.enums import ParseMode, MessageMediaType
from helper.database import db
from config import Config, Txt
from info import AUTH_CHANNEL
from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, is_req_subscribed, client, start_clone_bot, remove_path
from helper.ffmpeg import fix_thumb, take_screen_shot, change_metadata
import humanize



@Client.on_callback_query(filters.regex("renme"))
async def handle_re_callback(client, callback_query):
    user_id = callback_query.from_user.id

    parts = callback_query.data.split("_")
    if len(parts) != 3:
        return await callback_query.answer("Invalid callback data", show_alert=True)

    batch_no = int(parts[1])
    file_type_short = parts[2]
    file_type = "document" if file_type_short == "d" else "video"

    cursor = await db.get_batch_files(user_id, batch_no)
    files = await cursor.to_list(None)
    await callback_query.message.edit_text(f"Starting renaming for Batch #{batch_no}... Use `/process {batch_no}` To Restart Process Or If It Ended In Between.")
    if not files:
        return await callback_query.message.edit_text("No files found in this batch.")
    dump = await db.get_dump(user_id)
    for f in files:
        await client.send_message(user_id, "Processing next...")
        dummy_message = await client.get_messages(chat_id=1733124290, message_ids=f["file_id"])
        await process_queue(client, dummy_message, file_type, dump)
        
    await client.send_message(user_id, "Renaming Ended! \nClick On Delete Data If Renaming Ended Properly Else Use `/process {batch no}`. To Do Again",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Delete Data", callback_data=f"allinone_del_{batch_no}")]]
        )
    )
    

    


async def process_queue(bot, update, type, dump):
    client = bot
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")
    message = update
    if message.document:
        file_name = message.document.file_name
        fle_size = message.document.file_size
    elif message.video:
        file_name = message.video.file_name
        fle_size = message.video.file_size
    elif message.audio:
        file_name = message.audio.file_name
        fle_size = message.audio.file_size
        

    # Extracting necessary information
    prefix = await db.get_prefix(update.from_user.id)
    suffix = await db.get_suffix(update.from_user.id)
    swaps = await db.get_swaps(update.from_user.id)
    rep_data = await db.get_rep(update.from_user.id)
    try:
        fule_name = file_name.replace(rep_data['old'], rep_data['new'])
        if swaps:
            for old, new in swaps.items():
                fule_name = fule_name.replace(old, new)
        
    except Exception as e:
        await client.send_message(update.from_user.id, f"Error During Swap : {e}")
        pass
    new_name = fule_name.replace("_", " ")
    new_filename_ = new_name
    try:
        # adding prefix and suffix
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)

    except Exception as e:
        return await client.send_message(update.from_user.id, f"⚠️ Sᴏᴍᴇᴛʜɪɴ Wᴇɴᴛ Wʀᴏɴɢ CᴀN'ᴛ ʙʟᴇ Tᴏ Sᴇᴛ <b>Pʀᴇꜰɪx</b> oʀ <b>Sᴜꜰꜰɪx</b> ☹️ \n\n🎋Nᴇᴇᴅ Sᴜᴩᴩᴏʀᴛ, Fᴏʀᴡᴀʀᴅ Tʜɪꜱ Mᴇꜱꜱᴀɢᴇ Tᴏ Mʏ Cʀᴇᴀᴛᴏʀ <a href=https://t.me/Syd_Xyz>ᴍʀ ѕчδ 🌍</a>\nεɾɾσɾ: {e}")

    _bool_metadata = await db.get_metadata(update.from_user.id)

    
    
    file_path = f"downloads/{new_filename}"
    file = update

    ms = await client.send_message(update.from_user.id, f" __**Renaming \n{file_name} \nto \n{new_filename}**🥺__\n\n**Dᴏᴡɴʟᴏᴀᴅɪɴɢ....⏳**")
    try:
        path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=(f"\n⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n\n❄️ **Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
    except Exception as e:
        return await ms.edit(e)
    if (_bool_metadata):
        metadata_path = f"Metadata/{new_filename}" 
        metadata = await db.get_metadata_code(update.from_user.id)
        if metadata:
            await ms.edit("I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n__**Pʟᴇᴀsᴇ Wᴀɪᴛ...**__\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")            
            if await change_metadata(path, metadata_path, metadata):            
                await ms.edit("Metadata Added.....")
                print("Metadata Added.....")
        await ms.edit("**Metadata added to the file successfully ✅**\n\n⚠️ __**Please wait...**__\n\n**Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....**")
    else:
        await ms.edit("__**Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ...**😇__\n\n**Uᴩʟᴏᴀᴅɪɴɢ....🗯️**")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()

    except:
        pass
    ph_path = None
    media = getattr(file, file.media.value)

    c_caption = await db.get_caption(update.from_user.id)
    c_thumb = await db.get_thumbnail(update.from_user.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(
                media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇyᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")
    else:
        caption = f"**{new_filename}**"

    if (media.thumbs or c_thumb):
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
            width, height, ph_path = await fix_thumb(ph_path)
        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
            except Exception as e:
                ph_path = None
                print(e)

    if media.file_size > 2000 * 1024 * 1024:
        try:
            user_bot = await db.get_user_bot(Config.ADMIN[0])
            app = await start_clone_bot(client(user_bot['session']))

            if type == "document":

                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(f"⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

            elif type == "video":
                filw = await app.send_video(
                    Config.LOG_CHANNEL,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(f"⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)
            elif type == "audio":
                filw = await app.send_audio(
                    Config.LOG_CHANNEL,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(f"⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(dump, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    else:
        try:
            if type == "document":
                filw = await bot.send_document(
                    dump,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(f"⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))
                file_size = filw.document.file_size
            elif type == "video":
                filw = await bot.send_video(
                    dump,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    width=width,
                    height=height,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(f"⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                file_size = filw.video.file_size
            elif type == "audio":
                filw = await bot.send_audio(
                    dump,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(f"⚠️ __**Renaming \n{file_name} \nto \n{new_filename}**__\n🌨️ **Uᴩʟᴏᴀᴅɪɴ' Sᴛᴀʀᴛᴇᴅ....**", ms, time.time()))

                file_size = filw.audio.file_size
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    await ms.delete()
    if abs(file_size - fle_size) > 10 * 1024 * 1024:
        await client.send_message(update.from_user.id, f"{file_name} FOUND FILE SIZE ERROR. PLEASE RE RENAME AFTER CONFIRMING THERE IS AN ERROR")
        

    os.remove(file_path)
    if ph_path:
        os.remove(ph_path)
    if (_bool_metadata):
        os.remove(metadata_path)
    #if path:
        #os.remove(path)
   
                              



