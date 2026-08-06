from .BaseController import BaseController
from fastapi import UploadFile
from helpers.config import get_config


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.scale_mb = 1024 * 1024  # Scale factor for MB to bytes

    def validatefile(self, file: UploadFile):
        # Implement your file validation logic here
        if file.content_type not in self.config.FILE_ALLOWED_EXTENSIONS:
            return False, "Invalid file type"
        if file.size > self.config.FILE_MAX_SIZE * self.scale_mb:
            return False, "File size exceeds the maximum limit"

        return True
