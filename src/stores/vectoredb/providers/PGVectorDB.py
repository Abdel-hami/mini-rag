from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import VectorDBEnum, PgVectorIndexingTypeEnums, DistanceMethodEnum,PgVectorDistanceMethodEnums, PgVectorTableSchemeEnums
from models.db_schemes import RetrievedDocument
import logging
from typing import List
from sqlalchemy  import text as sql_text
import json
class PGVectorDB(VectorDBInterface):

    def __init__(self, db_client,default_vector_size:int, distance_method:str):
        self.db_client = db_client
        self.default_vector_size = default_vector_size

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = PgVectorDistanceMethodEnums.DOT.value

        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_index"
        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def disconnect(self):
        pass

  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    async def is_collection_existed(self, collection_name: str) -> bool:
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tables = sql_text("SELECT * FROM pg_tables where tablename = :collection_name")
                result = await session.execute(list_tables, {"collection_name": collection_name})
                record = result.scalar_one_or_none()
                # result = await session.execute(sql_text(f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = '{collection_name}');"))
                # return result.scalar_one()
        return record
    
    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tables = sql_text("SELECT * FROM pg_tables where tablename like :collection_name_prefix")
                result = await session.execute(list_tables, {"collection_name_prefix": self.pgvector_table_prefix })
                records = result.scalars().all()
        return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text(f'''
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes 
                    FROM pg_tables 
                    WHERE tablename = :collection_name
                ''')

                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')

                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
                record_count = await session.execute(count_sql)

                table_data = table_info.fetchone()
                if not table_data:
                    return None
                
                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename": table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4],
                    },
                    "record_count": record_count.scalar_one(),
                }

    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")
                stmt = sql_text("DROP TABLE IF EXISTS :collection_name")
                await session.execute(stmt, {"collection_name": collection_name})
        return True

    async def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        is_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_existed:
            async with self.db_client() as session:
                async with session.begin():
                    self.logger.info(f"Creating collection: {collection_name}")
                    stmt = sql_text(
                    f'create table {collection_name} ('
                        f'{PgVectorTableSchemeEnums.ID.value} bigserial primary key,'
                        f'{PgVectorTableSchemeEnums.TEXT.value} text,'
                        f'{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}),'
                        f'{PgVectorTableSchemeEnums.METADATA.value} jsonb default \'{{}}\',' ## !!!!!!!
                        f'{PgVectorTableSchemeEnums._prefix.value} text,'
                        f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer,'
                        f'forign key ({PgVectorTableSchemeEnums.CHUNK_ID.value}) references chunk(chunk_id)'
                        ')'
                    )
                    await session.execute(stmt)
            return True
        return False

    async def is_collection_indexed(self, collection_name: str) -> bool:
        is_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_existed:
            self.logger.error(f"Can not check index for non-existed collection: {collection_name}")
            return False
        index = self.default_index_name(collection_name=collection_name)
        async with self.db_client() as session:
            async with session.begin():
                stmt =sql_text("""
                    select indexname from pg_indexes where tablename = :collection_name""")
    async def insert_one(self, collection_name: str, text: str, vector: list,
                        metadata: dict = None, 
                        record_id: str = None):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk_id: {collection_name}")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                      f'({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                                      'VALUES (:text, :vector, :metadata, :chunk_id)'
                                      )
                
                metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata is not None else "{}"
                await session.execute(insert_sql, {
                    'text': text,
                    'vector': "[" + ",".join([ str(v) for v in vector ]) + "]",
                    'metadata': metadata_json,
                    'chunk_id': record_id
                })

        
        return True

    async def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50):
        
        is_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        if len (vectors) != len (record_ids):
            self.logger.error(f"Can not insert new record without chunk_id: {collection_name}")
            return False

        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)


        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_end = i + batch_size
                    batch_texts = texts[i:batch_end]
                    batch_vectors = vectors[i:batch_end]
                    batch_metadata = metadata[i:batch_end]
                    batch_record_ids = record_ids[i:batch_end]

                    values = {}
                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):
                        values.append({
                            "text": _text,
                            "vector": "[" + ",".join([ str(v) for v in _vector ]) + "]",
                            "metadata": json.dumps(_metadata, ensure_ascii=False) if _metadata is not None else "{}",
                            "chunk_id": _record_id
                        })
                    stmt = sql_text(f'INSERT INTO {collection_name} '
                                    f'({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                                    'VALUES (:text, :vector, :metadata, :chunk_id)'
                                    )
                    await session.execute(stmt, values)

        return True

    async def search_by_vector(self, collection_name: str, vector: list, limit: int) -> List[RetrievedDocument]:
        is_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        vector = "["+",".join([ str(v) for v in vector ])+"]"

        async with self.db_client() as session:
            async with session.begin():
                stmt = sql_text(
                    f'SELECT {PgVectorTableSchemeEnums.TEXT.value} as text, 1- ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vecoor) as score '
                    f'FROM {collection_name} lIMIT {limit}'
                )

                await session.execute(stmt, {"vecoor": vector})
                records = await session.fetchall() ## fetchall() returns a list of Row objects, not a list of dictionaries

        return [
            RetrievedDocument(
                text = r.text,
                score = r.score)
            for r in records
        ]