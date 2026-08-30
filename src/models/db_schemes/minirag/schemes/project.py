from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func # func is used to get the current time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
class Project(SQLAlchemyBase):

    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    peoject_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    # many-to-one
    assets = relationship("Asset", back_populates="project")
    chunks = relationship("DataChunk", back_populates="project")