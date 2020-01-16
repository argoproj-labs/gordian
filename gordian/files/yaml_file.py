from . import BaseFile
import yaml

class YamlFile(BaseFile):

    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)
        yaml.add_representer(type(None), represent_none)

    def load_objects(self):
        return list(yaml.safe_load_all(self.file_contents))

    def dump(self):
        return yaml.dump_all(self.objects, default_flow_style=False, explicit_start=True)

def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')