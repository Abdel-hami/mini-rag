from BaseController import BaseController
from ProjectController import ProjectController
from models.db_schemes.data_chunk import DataChunk
from models.db_schemes.project import Project
from stores.llm.LLMEnum import CohereInputType

class NLPController(BaseController):

    def __init__(self, vectordb_client, embedding_client, generation_client):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client

    def create_collection_name(project_id:str):
        return f"collection_{project_id}"

    def do_reset_collection(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vectordb_collection_info(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.get_collection_info(collection_name=collection_name)

    def index_to_vectordb(self, project:Project, chunks:list[DataChunk], do_reset:bool):

        #get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # manage items
        texts = [chunk.chunk_content for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]
        vectors = [self.embedding_client.embed_text(text=chunk.chunk_content, document_type=CohereInputType.SEARCH_DOCUMENT.value) for chunk in chunks]

        #create collection if not existed
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name, 
            embedding_size=self.embedding_client.embedding_size, 
            do_reset=do_reset)

        #insert
        _ =self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts, 
            vectors=vectors,
            metadata=metadata)
        
        return True
