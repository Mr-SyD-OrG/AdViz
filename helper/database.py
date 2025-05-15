import motor.motor_asyncio
from config import Config
from .utils import send_log
import datetime


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user
        self.bot = self.db.bots
        self.usr = self.db.usyds
        self.req = self.db.requests
        self.batches = self.db.batches
        self.active_batches = self.db.active_batches

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})
        
    async def del_join_req(self):
        await self.req.drop()
        
    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            prefix=None,
            suffix=None,
            new=None,
            old=None,
            dump=int(id),
            metadata=False,
            metadata_code=""" -map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- " -metadata author="@" -metadata:s:s title="Subtitled By :- @" -metadata:s:a title="By :- @" -metadata:s:v title="By:- @" """
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)
                                     
    async def add_swap(self, user_id: int, key: str, value: str):
        await self.usr.update_one(
            {"_id": user_id},
            {"$set": {f"swaps.{key}": value}},
            upsert=True
        )
    
    async def delete_batch(self, user_id: int, batch_no: int):
        result = await self.batches.delete_many({
             "user_id": user_id,
             "batch_no": batch_no
        })
        return result.deleted_count


    async def delete_swap(self, user_id: int, key: str):
        await self.usr.update_one(
            {"_id": user_id},
            {"$unset": {f"swaps.{key}": ""}}
        )

    async def get_swaps(self, user_id: int) -> dict:
        user = await self.usr.find_one({"_id": user_id})
        return user.get("swaps", {}) if user else {}

    async def add_user_bot(self, bot_datas):
        if not await self.is_user_bot_exist(bot_datas['user_id']):
            await self.bot.insert_one(bot_datas)

    async def get_user_bot(self, user_id: int):
        user = await self.bot.find_one({'user_id': user_id, 'is_bot': False})
        return user if user else None

    async def is_user_bot_exist(self, user_id):
        user = await self.bot.find_one({'user_id': user_id, 'is_bot': False})
        return bool(user)

    async def remove_user_bot(self, user_id):
        await self.bot.delete_many({'user_id': int(user_id), 'is_bot': False})

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def set_rep(self, id, sydd, syddd):
        await self.col.update_one(
            {'_id': int(id)},  # Find the document by its ID
            {'$set': {'old': sydd, 'new': syddd}}  # Update 'sydd' and 'syddd' fields
        )

    async def set_dump(self, id, dump: int):
        await self.col.update_one({'_id': int(id)}, {'$set': {'dump': int(dump)}})

    async def get_dump(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('dump', int(id))   
   
    async def set_active_batch(self, user_id: int, batch_no: int):
        await self.active_batches.update_one(
            {"user_id": user_id},
            {"$set": {"batch_no": batch_no}},
            upsert=True
        )

    async def get_active_batch(self, user_id: int):
        doc = await self.active_batches.find_one({"user_id": user_id})
        return doc["batch_no"] if doc else None

    async def clear_active_batch(self, user_id: int):
        await self.active_batches.delete_one({"user_id": user_id})

    async def add_file_to_batch(self, user_id: int, batch_no: int, file_id: str, file_name: str, file_type: str):
        await self.batches.insert_one({
            "user_id": user_id,
            "batch_no": batch_no,
            "file_id": file_id,
            "file_name": file_name,
            "file_type": file_type
        })

    async def get_batch_files(self, user_id: int, batch_no: int):
        return self.batches.find({"user_id": user_id, "batch_no": batch_no})


    async def get_rep(self, id):
        user = await self.col.find_one({'_id': int(id)})
        if user:  # Check if the document exists
            return {
                'old': user.get('old', ""),   # Default to an empty string if 'sydd' is not found
                'new': user.get('new', "")  # Default to an empty string if 'syddd' is not found
            }
        return {'old': "", 'new': ""}  # Default return if the document doesn't exist


    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    async def set_prefix(self, id, prefix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'prefix': prefix}})

    async def get_prefix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('prefix', None)

    async def set_suffix(self, id, suffix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'suffix': suffix}})

    async def get_suffix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('suffix', None)

    async def remove_batch(self, user_id: int, batch_no: int):
        await self.batches.delete_many({"user_id": user_id, "batch_no": batch_no})

    async def set_metadata(self, id, bool_meta):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata': bool_meta}})

    async def get_metadata(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata', None)

    async def set_metadata_code(self, id, metadata_code):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata_code': metadata_code}})

    async def get_metadata_code(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata_code', None)


db = Database(Config.DB_URL, Config.DB_NAME)
