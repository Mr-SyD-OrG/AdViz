from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
import re

def extract_episode_number(filename):    
    match = re.search(pattern1, filename)
    if match:
        print("Matched Pattern 1")
        return match.group(2)  # Extracted episode number
    
    # Try Pattern 2
    match = re.search(pattern2, filename)
    if match:
        print("Matched Pattern 2")
        return match.group(2)  # Extracted episode number

    # Try Pattern 3
    match = re.search(pattern3, filename)
    if match:
        print("Matched Pattern 3")
        return match.group(1)  # Extracted episode number

    # Try Pattern 3_2
    match = re.search(pattern3_2, filename)
    if match:
        print("Matched Pattern 3_2")
        return match.group(1)  # Extracted episode number
        
    # Try Pattern 4
    match = re.search(pattern4, filename)
    if match:
        print("Matched Pattern 4")
        return match.group(2)  # Extracted episode number

    # Try Pattern X
    match = re.search(patternX, filename)
    if match:
        print("Matched Pattern X")
        return match.group(0)  # Extracted episode number
        
    return "None"
async def features_button(user_id):
    metadata = await db.get_metadata(user_id)

    button = [[
        InlineKeyboardButton(
            'ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='filters_metadata'),
        InlineKeyboardButton('✅' if metadata else '❌',
                             callback_data='filters_metadata')
    ]
    ]

    return InlineKeyboardMarkup(button)


@Client.on_callback_query(filters.regex('^filters'))
async def handle_filters(bot: Client, query: CallbackQuery):
    user_id = query.from_user.id
    type = query.data.split('_')[1]
    if type == 'metadata':
        get_meta = await db.get_metadata(user_id)

        if get_meta:
            await db.set_metadata(user_id, False)
            markup = await features_button(user_id)
            await query.message.edit_reply_markup(markup)
        else:
            await db.set_metadata(user_id, True)
            markup = await features_button(user_id)
            await query.message.edit_reply_markup(markup)
