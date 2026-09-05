from typing import List

from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessingEnum
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dataclasses import dataclass
import os


@dataclass
class Document:
    page_content: str
    metadata: dict

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

        if not os.path.exists(file_path):
            return None
        
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        
        return None
    
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)
        if loader:
            return loader.load()
        
        return None

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

        # chunks = text_splitter.create_documents(
        #     file_texts,
        #     metadatas= file_metadata)
        chunks = self.simple_text_processer(
            texts=file_texts,
            metadata=file_metadata,
            chunk_size=chunk_size,
            tag_spliter="\n"
        )

        return chunks

    def simple_text_processer(self, texts: List[str], metadata:dict, chunk_size:int, tag_spliter:str = "\n"):

        full_text = "\n".join(texts)

        lines = [doc.strip() for doc in full_text.split(tag_spliter) if len(doc.strip())>1]

        chnks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + tag_spliter

            if len(current_chunk) > chunk_size:
                chnks.append(Document(current_chunk, metadata))
                current_chunk = ""

        if len(current_chunk) > 0:
            chnks.append(Document(current_chunk, metadata))

        return chnks