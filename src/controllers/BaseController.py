from helpers.config import Config, get_config

class BaseController:
    def __init__(self):
        self.config = get_config()