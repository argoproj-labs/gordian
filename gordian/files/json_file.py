from . import BaseFile
import json

class JsonFile(BaseFile):

    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)

    def _load_objects(self):
        return json.loads(self.file_contents)

    def _dump(self):
        return json.dumps(self.objects, indent=4)
