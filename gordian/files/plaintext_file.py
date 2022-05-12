from . import BaseFile


class PlainTextFile(BaseFile):
    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)

    def _load_objects(self):
        return self.file_contents

    def _dump(self, serialize_options={}):
        return self.file_contents
