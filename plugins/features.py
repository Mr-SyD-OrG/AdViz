from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
import re

# Pattern 1: S01E02 or S01EP02
pattern1 = re.compile(r'S(\d+)(?:E|EP)(\d+)')
# Pattern 2: S01 E02 or S01 EP02 or S01 - E01 or S01 - EP02
pattern2 = re.compile(r'S(\d+)\s*(?:E|EP|-\s*EP)(\d+)')
# Pattern 3: Episode Number After "E" or "EP"
pattern3 = re.compile(r'(?:[([<{]?\s*(?:E|EP)\s*(\d+)\s*[)\]>}]?)')
# Pattern 3_2: episode number after - [hyphen]
pattern3_2 = re.compile(r'(?:\s*-\s*(\d+)(?!p)\s*)')
# Pattern 4: S2 09 ex.
pattern4 = re.compile(r'S(\d+)\s*[-E ]\s*(\d+)', re.IGNORECASE)
# Pattern X: Standalone Episode Number
patternX = re.compile(r'\b(?!\d{3,4}p\b)\d{3,4}\b', re.IGNORECASE)

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
