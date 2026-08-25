from models.db_schemes import Asset
from models.BaseDataModel import BaseDataModel
from models import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.ASSET_COLLECTION_NAME.value]


    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance


    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.ASSET_COLLECTION_NAME.value not in all_collections:
            self.collection =await self.db_client.create_collection(DataBaseEnum.ASSET_COLLECTION_NAME.value)
            indexes =  Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_asset(self, asset:Asset):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_none=True))
        asset.id = result.inserted_id

        return asset
    ## add filtering by aset type
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str = None):

        records =  await self.collection.find(
            {"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type}
            ).to_list(length=None)

        return [Asset(**record) for record in records]

    async def get_project_record(self, project_id: str, asset_name:str):

        record = await self.collection.find_one({"asset_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id, "asset_name": asset_name})
        if not record:
            return None
        return Asset(**record)
    