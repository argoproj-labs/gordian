import unittest
from unittest.mock import MagicMock
from gordian.repo import Repo
from gordian.files import YamlFile
from .utils import Utils

class TestBaseFile(unittest.TestCase):

    def setUp(self):
        self.github_file = Utils.create_github_content_file()
        self.mock_git = MagicMock()
        self.repo = Repo('test', git=self.mock_git)
        self.base_file = YamlFile(self.github_file, self.repo)

    def test_iterable(self):
        assert(iter(self.base_file))

