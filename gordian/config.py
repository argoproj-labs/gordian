import yaml

class Config:

    def __init__(self, config_file):
        self.config_file = config_file

    def get_data(self):
        with open(self.config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        return data_loaded