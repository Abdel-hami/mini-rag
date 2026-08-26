from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, String, Integer, DateTime, func , ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID,JSONB
import uuid
from sqlalchemy import Index
from pydantic import BaseModel

class DataChunk(SQLAlchemyBase):

    __tablename__ = "chunks"

    data_chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    data_chunk_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    data_chunk_text = Column(String, nullable=False)
    data_chunk_metadata = Column(JSONB, nullable=True)
    data_chunk_order = Column(Integer, nullable=False)

    data_chunk_project_id = Column(Integer,ForeignKey("projects.project_id"), nullable=False)
    data_chunk_asset_id = Column(Integer,ForeignKey("assets.asset_id"), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    project = relationship("Project", back_populates="chunks")
    asset = relationship("Asset", back_populates="chunks")

    __table_args__ = (
        Index("ix_data_chunk_project_id", data_chunk_project_id),
        Index("ix_data_chunk_asset_id", data_chunk_asset_id)
    )

class RetrievedDocument(BaseModel):
    text: str 
    score: float
    ## then we can add metadata and so on