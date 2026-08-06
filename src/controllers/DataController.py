from .BaseController import BaseController
from fastapi import UploadFile
from helpers.config import get_config
from models import ResponseSignal
import re

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

    def generate_unique_name
    def clean_filename(self, filename: str) -> str:
        # Remove any special car except undercore and .
        cleaned_filename = re.sub(r'[^a-zA-Z0-9_.]', '', filename)
        #replace spaces with underscores
        cleaned_filename = cleaned_filename.replace(' ', '_')
        return cleaned_filename