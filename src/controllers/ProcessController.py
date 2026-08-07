from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessingEnum
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

class ProcessController(BaseController):
    def __init__(self, project_id:str):
        super().__init__()
        self.project_id = project_id
        self.file_path = ProjectController().get_project_path(project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id:str):
        file_path = os.path.join(self.file_path, file_id)
        file_ext = self.get_file_extension(file_id)

        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        
        return None
    
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)
        return loader.load()

    def process_file_content(self, file_content:list,file_id: str, chunk_size: int, overlap_size: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size, 
            length_function=len)

        file_texts = [
            doc.page_content
            for doc in file_content
        ]

        file_metadata = [
            doc.metadata
            for doc in file_content
        ]

        chunks = text_splitter.create_documents(
            file_texts,
            metadatas= file_metadata)

        return chunks