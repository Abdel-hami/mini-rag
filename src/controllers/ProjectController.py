
from .BaseController import BaseController
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    
    def get_project_path(self, project_id:str):

        projec_dir = os.path.join(self.files_dir, str(project_id))
        if not os.path.exists(projec_dir):
            os.makedirs(projec_dir)
        return projec_dir