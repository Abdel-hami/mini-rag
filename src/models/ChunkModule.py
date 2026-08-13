from models.db_schemes.data_chunk import DataChunk
from models.BaseDataModel import BaseDataModel
from models import DataBaseEnum
from pymongo import InsertOne


class ChnukModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.CHUNK_COLLECTION_NAME.value]

    async def create_chunk(self, chunk:DataChunk):
        chunk = await self.collection.insert_one(chunk.model_dump())
        chunk.id = chunk.inserted_id

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
                InsertOne(chunk.model_dump())
                for chunk in batch
            ] 
            # print(operations)

            await self.collection.bulk_write(operations) ## bulk write: it is a way to insert multiple documents in a single operation

        return len(chunks)

    async def delete_chunk_by_project_id(self, project_id: str):
        reuslt =await self.collection.delete_many({"chunk_project_id": project_id})
        return reuslt.deleted_count