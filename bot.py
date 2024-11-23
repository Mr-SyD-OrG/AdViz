import logging
import logging.config
import warnings
from pyrogram import Client, idle, filters
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from plugins.web_support import web_server
from pytz import timezone
from datetime import datetime
import asyncio
import os
from threading import Thread
from time import sleep
import pyromod
from mrsyd import start_forwarding_thread, file_queue


if not os.path.exists("received_files"):
    os.makedirs("received_files")

CHANNELS = ["-1002464733363", "-1002429058090", "-1002433450358"]
MSYD = -1002377676305

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.ERROR)


class Bot(Client):

    def __init__(self):
        super().__init__(
            name="SnowRenamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.force_channel = Config.FORCE_SUB
        if Config.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Config.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                logging.warning(e)
                logging.warning("Make Sure Bot admin in force sub channel")
                self.force_channel = None
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Config.PORT).start()
        logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")

        for id in Config.ADMIN:
            try:
                await self.send_message(id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")
            except:
                pass

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(Config.LOG_CHANNEL, f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`</b>")
            except:
                print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")
        start_forwarding_thread(self)

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")
        
    @Client.on_message(filters.document | filters.audio | filters.video)
    def handle_file(self, client, message):
        if message.chat.id == MSYD:  # Ensure the file is from the specified chat
            try:
                file_id = message.document.file_id
                file_name = message.document.file_name if message.document else "unknown_file"
                
                # Download the file to the "received_files" directory
                message.download(file_name=f"received_files/{file_name}")
                
                # Add the file ID to the queue for forwarding
                file_queue.append(file_id)
                logging.info(f"File {file_name} received and added to the queue.")
            except Exception as e:
                logging.error(f"Error receiving file: {e}")


bot = Bot()
bot.run()
