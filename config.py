import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # pyro client config
    API_ID = os.environ.get("API_ID", "")  # ⚠️ Required
    API_HASH = os.environ.get("API_HASH", "")  # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # ⚠️ Required

    # database config
    DB_NAME = os.environ.get("DB_NAME", "cluster0")
    DB_URL = os.environ.get("DB_URL", "")  # ⚠️ Required

    SUPPORT = os.environ.get("SUPPORT", "syd_xyz") #Without @ Or Modify
    UPDATES = os.environ.get("UPDATES", "syd_xyz") #Without @

    # other configs
    BOT_UPTIME = time.time()
    PICS = os.environ.get("PICS", 'https://graph.org/file/8c8372dfa0e0ddf8da91d.jpg https://graph.org/file/3b2b8110f6f57f7fc5c74.jpg  https://graph.org/file/1bd6fa19297caf4189c61.jpg  ').split()
    ADMIN = [int(admin) if id_pattern.search(
        admin) else admin for admin in os.environ.get('ADMIN', '').split()]  # ⚠️ Required

    FORCE_SUB = os.environ.get("FORCE_SUB", "") # ⚠️ Required Username without @
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))  # ⚠️ Required
    FLOOD = int(os.environ.get("FLOOD", '10'))
    BANNED_USERS = set(int(x) for x in os.environ.get(
        "BANNED_USERS", "1234567890").split())

    # wes response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8080"))


class Txt(object):
    # part of text configuration
    START_TXT = """<b>Hᴇʏ {} 👋,
ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {} ᴡᴏʀʟᴅ'ꜱ ꜰɪʀꜱᴛ ꜰʀᴇᴇ ʙᴀɴ-ꜱᴩᴀᴍ ʙᴏᴛ

ʙʏ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ, ʏᴏᴜ ᴀɢʀᴇᴇ ᴛᴏ ᴀʟʟ ᴛᴇʀᴍꜱ ᴀɴᴅ ꜱᴇʀᴠɪᴄᴇ ᴄᴏɴᴅɪᴛɪᴏɴꜱ ᴍᴇɴᴛɪᴏɴᴇᴅ ɪɴ @VeeADTnS

ꜱᴛᴀʀᴛ ʏᴏᴜʀ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴛʜɪɴɢꜱ ᴜꜱɪɴɢ /add_account</b>"""

    ABOUT_TXT = """<b>╭───────────⍟
➥ ᴍy ɴᴀᴍᴇ : {}
➥ Pʀᴏɢʀᴀᴍᴇʀ : <a href=https://t.me/vizean>Vɪᴢᴇᴀɴ</a> 
➥ Cᴏᴅᴇᴅ : ᴍʀ ꜱʏᴅ
➥ Lᴀɴɢᴜᴀɢᴇ : ᴩʏᴛʜᴏɴ3
➥ Dᴀᴛᴀ Bᴀꜱᴇ: ᴍᴏɴɢᴏᴅʙ
➥ ᴍʏ ꜱᴇʀᴠᴇʀ : ᴩʀɪᴠᴀᴛᴇ
➥ Vᴇʀsɪᴏɴ : v1.0
╰───────────────⍟ """

    HELP_TXT = """

<b>Tɪᴇʀ : Fʀᴇᴇ</b>
<b>• ᴀᴄᴄᴏᴜɴᴛ : 1</b> 
<b>• ɢʀᴏᴜᴩꜱ : 3</b> 
<b>• ᴄᴜꜱᴛᴏᴍ ʙɪᴏ ᴄʜᴀɴɢᴇ : ʏᴇꜱ</b> 
<b>• ᴛɪᴍᴇ ɪɴᴛᴇʀᴠᴀʟ : 2ʜʀꜱ </b> 

<b>Tɪᴇʀ : Pʀᴇᴍɪᴜᴍ</b>
<b>• ᴀᴄᴄᴏᴜɴᴛ : ᴜɴʟɪᴍɪᴛᴇᴅ</b> 
<b>• ɢʀᴏᴜᴩꜱ : ᴜɴʟɪᴍɪᴛᴇᴅ</b> 
<b>• ᴄᴜꜱᴛᴏᴍ ʙɪᴏ ᴄʜᴀɴɢᴇ : ɴᴏ</b> 
<b>• ᴛɪᴍᴇ ɪɴᴛᴇʀᴠᴀʟ : ᴄᴜꜱᴛᴏᴍ </b>

<u><b><blockquote>Jᴜꜱᴛ ꜱᴇɴᴅ ᴛʜᴇ ᴩɪᴄᴛᴜʀᴇ.. ⚡</blockquote></u></b>

◽ <b><u>Hᴏᴡ Tᴏ Sᴇᴛ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ</u></b>

<b>•></b> /set_caption - Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Sᴇᴛ ᴀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
<b>•></b> /see_caption - Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Vɪᴇᴡ Yᴏᴜʀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
<b>•></b> /del_caption - Uꜱᴇ Tʜɪꜱ Cᴏᴍᴍᴀɴᴅ Tᴏ Dᴇʟᴇᴛᴇ Yᴏᴜʀ Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ
Exᴀᴍᴩʟᴇ:- <code> /set_caption 📕 Fɪʟᴇ Nᴀᴍᴇ: {filename}
💾 Sɪᴢᴇ: {filesize}
⏰ Dᴜʀᴀᴛɪᴏɴ: {duration} </code>

◽ <b><u>Hᴏᴡ Tᴏ Rᴇɴᴀᴍᴇ A Fɪʟᴇ</u></b>
<b>•></b> Sᴇɴᴅ Aɴy Fɪʟᴇ Aɴᴅ Tyᴩᴇ Nᴇᴡ Fɪʟᴇ Nᴀᴍᴇ \nAɴᴅ Sᴇʟᴇᴄᴛ Tʜᴇ Fᴏʀᴍᴀᴛ [ document, video, audio ].           

◽ <b><u>Sᴇᴛ ꜱᴜꜰꜰɪx ᴀɴᴅ ᴩʀᴇꜰɪx.</b></u>
<b>•></b> /set_prefix - Sᴇᴛ ᴩʀᴇꜰɪx(ꜰɪʀꜱᴛ ᴡᴏʀᴅ)
<b>•></b> /set_suffix - Sᴇᴛ ꜱᴜꜰꜰɪx(ʟᴀꜱᴛ ᴡᴏʀᴅ)
<b>•></b> /see_prefix - Sᴇᴇ ᴩʀᴇꜰɪx
<b>•></b> /see_suffix - Sᴇᴇ ꜱᴜꜰꜰɪx
<b>•></b> /del_prefix - Dᴇʟᴇᴛᴇ ᴩʀᴇꜰɪx
<b>•></b> /del_suffix - Dᴇʟᴇᴛᴇ ꜱᴜꜰꜰɪx

<b>⦿ Developer:</b> <a href=https://t.me/SyD_Xyz>🔅 ᴍ.ʀ Sʏᦔ 🔅</a>
"""

    
    STATS_TXT = """
╔════❰ Sᴇʀᴠᴇʀ sᴛᴀᴛS  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ ᴜᴩᴛɪᴍᴇ: `{0}`
║┣⪼ ᴛᴏᴛᴀʟ sᴘᴀᴄᴇ: `{1}`
║┣⪼ ᴜsᴇᴅ: `{2} ({3}%)`
║┣⪼ ꜰʀᴇᴇ: `{4}`
║┣⪼ ᴄᴘᴜ: `{5}%`
║┣⪼ ʀᴀᴍ: `{6}%`
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪        
"""

    
