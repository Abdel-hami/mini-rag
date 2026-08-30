from models.db_schemes import Asset
from models.BaseDataModel import BaseDataModel
from models import DataBaseEnum
from bson import ObjectId
from sqlalchemy import select

class AssetModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client = db_client


    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset:Asset):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset

    ## add filtering by aset type
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str = None):
        async with self.db_client() as session:
            query = select(Asset).where(Asset.asset_project_id == asset_project_id, Asset.asset_type == asset_type)
            result = await session.execute(query)
            records = result.scalars().all()
            return records

    async def get_asset_record(self, project_id: str, asset_name:str):
        async with self.db_client() as session:
            query = select(Asset).where(Asset.asset_project_id == project_id, Asset.asset_name == asset_name)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record is None:
                return None
            return record

    