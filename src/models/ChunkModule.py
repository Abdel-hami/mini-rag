from models.db_schemes import DataChunk
from models.BaseDataModel import BaseDataModel
from models import DataBaseEnum
from pymongo import InsertOne
from sqlalchemy import select, delete, func

class ChnukModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client = db_client


    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        return instance

    async def create_chunk(self, chunk:DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.refresh(chunk)
        return chunk


    async def get_chunk(self, chunk_id: str):
        async with self.db_client() as session:
            result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
            chunk = result.scalar_one_or_none()
            if chunk is None:
                return None
            return chunk

    ## bulk write or batch write

    # give bulk write to each batch

    async def insert_many_chunks(self, chunks:list, batch_size:int =100):

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0,len(chunks), batch_size):
                    batch = chunks[i: i+batch_size]
                    session.add_all(batch)
        return len(chunks)

    async def delete_chunk_by_project_id(self, project_id: str):
        async with self.db_client() as session:
            statement = delete(DataChunk).where(DataChunk.data_chunk_project_id == project_id)
            result = await session.execute(statement)
            await session.commit()
        return result.rowcount
        # reuslt =await self.collection.delete_many({"chunk_project_id": project_id})
        # return reuslt.deleted_count

    async def get_all_chunk_by_project_id(self, project_id: str, page:int =1, page_size:int =15):
        async with self.db_client() as session:
            statement = select(DataChunk).where(DataChunk.data_chunk_project_id == project_id).offset((page-1)*page_size).limit(page_size)
            result = await session.execute(statement)
            records = result.scalars().all()
            return records

    async def get_total_chunks_count_by_project(self, project_id: str):
        total_count = 0
        async with self.db_client() as session:
            stmt = select(func.count(DataChunk.data_chunk_id)).where(DataChunk.data_chunk_project_id == project_id)
            result = await session.execute(stmt)
            total_count = result.scalar()
        return total_count