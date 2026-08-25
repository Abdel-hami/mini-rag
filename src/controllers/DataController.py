from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from helpers.config import get_config
from models import ResponseSignal
import re
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.scale_mb = 1024 * 1024  # Scale factor for MB to bytes

    def validatefile(self, file: UploadFile):
        # Implement your file validation logic here
        if file.content_type not in self.config.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.config.FILE_MAX_SIZE * self.scale_mb:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESSFULLY.value

    def generate_unique_filepath(self, filename: str, project_id: str) -> str:
        unique_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
        cleaned_filename = self.clean_filename(filename)

        new_file_path = os.path.join(project_path,unique_key + "_" + cleaned_filename)

        while os.path.exists(new_file_path):
            unique_key = self.generate_random_string()
            new_file_path = os.path.join(project_path, unique_key + "_" + cleaned_filename)

        return new_file_path, unique_key + "_" + cleaned_filename

    def clean_filename(self, filename: str) -> str:
        # Remove any special car except undercore and .
        cleaned_filename = re.sub(r'[^a-zA-Z0-9_.]', '', filename)
        #replace spaces with underscores
        cleaned_filename = cleaned_filename.replace(' ', '_')
        return cleaned_filename