import logging

logger = logging.getLogger(__name__)

class BaseFile:

    def __init__(self, github_file, repo, start=0):
        self.github_file = github_file
        self.repo = repo
        self.num = start
        self.file_contents = github_file.decoded_content
        self.objects = self._load_objects()

    def __iter__(self):
        return self

    def __next__(self):
        if self.num == len(self.objects):
            raise StopIteration

        num = self.num
        self.num += 1
        return self.objects[num]

    def save(self, message, dry_run):
        self.repo.update_file(self.github_file, self._dump(), message, dry_run)

    def _load_objects(self):
        raise NotImplementedError

    def _dump(self):
        raise NotImplementedError
