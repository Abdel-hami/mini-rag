from controllers.BaseController import BaseController
from models.db_schemes import DataChunk
from models.db_schemes import Project
from stores.llm.LLMEnum import CohereInputType
import json
class NLPController(BaseController):

    def __init__(self, vectordb_client, embedding_client, generation_client, template_parser):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self,project_id:str):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}"

    async def do_reset_collection(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)

    async def get_vectordb_collection_info(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_infos = await self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(
                collection_infos, default=lambda x:x.__dict__
            )
            
        )

    async def index_to_vectordb(self, project:Project, chunks:list[DataChunk],chunk_ids:list, do_reset:bool=False):

        #get collection name
        collection_name = self.create_collection_name(project_id=str(project.project_id))

        # manage items
        texts = [chunk.data_chunk_text for chunk in chunks]
        metadata = [chunk.data_chunk_metadata for chunk in chunks]
        vectors = self.embedding_client.embed_text(text=texts , document_type=CohereInputType.SEARCH_DOCUMENT.value)


        #create collection if not existed
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name, 
            embedding_size=self.embedding_client.embedding_size, 
            do_reset=do_reset)

        #insert
        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts, 
            vectors=vectors,
            metadata=metadata,
            record_ids=chunk_ids
            )
        
        return True


    async def search_vectordb_collection(self,project:Project, text:str, limit:int=5):
        #1- get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        query_vector = None

        #2- get query vector
        vectors = self.embedding_client.embed_text(text=text, document_type=CohereInputType.SEARCH_QUERY.value)

        if not vectors or len(vectors) == 0:
            return False

        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0]
        if not query_vector:
            return False

        #3- semantic search in vector db        
        results = await self.vectordb_client.search_by_vector(collection_name=collection_name, vector=query_vector, limit=limit)

        if not results:
            return False
        
        return json.loads(
            json.dumps(
                results, default=lambda x:x.__dict__
            )
        )

    async def answer_rag_question(self,project:Project, query:str, limit:int=2):
        retrieved_results = await self.search_vectordb_collection(project=project, text=query, limit=limit)
        # print(retrieved_results)
        if not retrieved_results:
            return "no retrieved results"

        system_prompt = self.template_parser.get_template("rag", "system_prompt")

        
        document_prompt = "\n".join([
            self.template_parser.get_template("rag", "document_prompt", {
                "doc_num":id+1,
                "chunk_text":self.generation_client.process_text(chunk["text"])})
            for id,chunk in enumerate(retrieved_results)
        ])

        footer_template = self.template_parser.get_template("rag", "footer_prompt", {"query":query})

        chat_history = [
            self.generation_client.construct_prompt(system_prompt, self.generation_client.enums.SYSTEM.value),
        ]
        full_prompt = "\n\n".join([document_prompt, footer_template])
        result = self.generation_client.generate_text(prompt=full_prompt,chat_history=chat_history)

        return result, full_prompt, chat_history