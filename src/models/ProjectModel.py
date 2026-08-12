from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from models.db_schemes.project import Project

class ProjectModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.PPROJECT_COLLECTION_NAME.value]

    async def create_project(self, project:Project):
        result = await self.collection.insert_one(project.model_dump())
        project.id = result.inserted_id

        return project 


    async def get_project_or_get_one(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id})

        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project)
            return project

        return Project(**record)

    async def get_all_projects(self, page:int=1, page_size:int=10):
        ## pagination: it is a technique to divide the data into pages and retrieve them one by one

        total_documents = self.collection.count_documents({})

        ## calculate total pages 
        total_pages = total_documents  // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find({}).skip((page - 1) * page_size).limit(page_size) # skip the first n documents

        projects = []
        async for project in cursor:
            projects.append(Project(**project))

        return projects

        

    