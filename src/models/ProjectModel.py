from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from models.db_schemes import Project
from sqlalchemy import select, func
class ProjectModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        # await instance.init_collection()
        return instance


    # async def init_collection(self):
    #     all_collections = await self.db_client.list_collection_names()
    #     if DataBaseEnum.PPROJECT_COLLECTION_NAME.value not in all_collections:
    #         self.collection = await self.db_client.create_collection(DataBaseEnum.PPROJECT_COLLECTION_NAME.value)
    #         indexes = Project.get_indexes()
    #         for index in indexes:
    #             await self.collection.create_index(
    #                 index["key"], name=index["name"], unique=index["unique"]
    #             )

    async def create_project(self, project:Project):
        # result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_none=True)) #mongo create _id here, insert_one returns the inserted id, the model_dump() returns a dictionary
        # # insert_one doesn't return the document you inserted. It returns an InsertOneResult object — a small object describing what happened, with two useful attributes:
        # # result.inserted_id → the ObjectId MongoDB generated (or the one you provided) for the new document
        # # result.acknowledged → bool, whether the write was acknowledged by the server


        # ## project.dump() returns a dictionary
        # #by_alias=True → key becomes _id instead of id
        # #exclude_none=True → drops _id: None when id isn't set, so MongoDB generates a real ObjectId
        # project.project_id = result.inserted_id # copy it back onto  Python object

        # return project 


        async with self.db_client() as session:
        # 'async with' guarantees context teardown and avoids connection leaks
            async with session.begin():
                await session.add(project)
            await session.commit()
            await session.refresh(project)
        return project


    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                #await
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if project is None:
                    record = Project(project_id=project_id)
                    project = await self.create_project(record)
                    return project
                else:
                    return project
                

    async def get_all_projects(self, page:int=1, page_size:int=10):
        ## pagination: it is a technique to divide the data into pages and retrieve them one by one
        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(select(func.count(Project.project_id)))
                total_documents = total_documents.scalar_one()
                total_pages = total_documents  // page_size
                if total_documents % page_size > 0:
                    total_pages += 1
                query = select(Project).offset((page-1)*page_size).limit(page_size)
                projects = await session.execute(query).scalars().all()

                return projects, total_pages
            

        

    