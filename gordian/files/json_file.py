from . import BaseFile
import json

class JsonFile(BaseFile):

    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)

    def load_objects(self):
        return json.loads(self.file_contents)

    def dump(self):
        return json.dumps(self.objects, indent=4)
