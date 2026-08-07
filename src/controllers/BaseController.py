from helpers.config import Config, get_config
import os
import random
import string

class BaseController:
    def __init__(self):
        self.config = get_config()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))  # Get the base directory of the project
        self.files_dir = os.path.join(self.base_dir, "assets/files")  # Directory to store uploaded files

    def generate_random_string(self, length=12):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))  # Generate a random string of fixed length(letters) for i in range(length))