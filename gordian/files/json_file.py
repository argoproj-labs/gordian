from . import BaseFile
import json


class JsonFile(BaseFile):
    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)

    def _load_objects(self):
        return json.loads(self.file_contents)

    def _dump(self, serialize_options={}):
        indent = serialize_options.get("indent", 4)
        return json.dumps(self.objects, indent=indent)
