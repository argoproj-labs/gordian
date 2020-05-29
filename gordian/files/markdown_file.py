from . import BaseFile

class MarkdownFile(BaseFile):

    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)

    def _load_objects(self):
        return self.file_contents.split(b'\n')

    def _dump(self):
        return b'\n'.join(self.file_contents)
