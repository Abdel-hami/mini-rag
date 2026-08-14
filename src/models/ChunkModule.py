from models.db_schemes.data_chunk import DataChunk
from models.BaseDataModel import BaseDataModel
from models import DataBaseEnum
from pymongo import InsertOne


class ChnukModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.CHUNK_COLLECTION_NAME.value]


    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance


    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.CHUNK_COLLECTION_NAME.value not in all_collections:
            self.collection =await self.db_client.create_collection(DataBaseEnum.CHUNK_COLLECTION_NAME.value)
            indexes =  DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_chunk(self, chunk:DataChunk):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_none=True))
        chunk.id = result.inserted_id

        return chunk

    async def get_chunk(self, chunk_id: str):
        chunk = await self.collection.find_one({"chunk_id": chunk_id})
        if chunk is None:
            return None

        return DataChunk(**chunk)

    ## bulk write or batch write

    # give bulk write to each batch

    async def insert_many_chunks(self, chunks:list, batch_size:int =100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_none=True))
                for chunk in batch
            ] 
            # print(operations)

            await self.collection.bulk_write(operations) ## bulk write: it is a way to insert multiple documents in a single operation

        return len(chunks)

    async def delete_chunk_by_project_id(self, project_id: str):
        reuslt =await self.collection.delete_many({"chunk_project_id": project_id})
        return reuslt.deleted_count