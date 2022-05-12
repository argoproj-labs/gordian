import unittest
from unittest.mock import MagicMock
from gordian.repo import Repo
from gordian.files import YamlFile
from .utils import Utils


class TestBaseFile(unittest.TestCase):
    def setUp(self):
        self.github_file = Utils.create_github_content_file()
        self.mock_git = MagicMock()
        self.repo = Repo("test", github=self.mock_git)
        self.base_file = YamlFile(self.github_file, self.repo)

    def test_iterable(self):
        assert iter(self.base_file)


class TestYamlFile(unittest.TestCase):
    def setUp(self):
        self.github_file = Utils.create_github_content_file()
        self.mock_git = MagicMock()
        self.repo = Repo("test", github=self.mock_git)
        self.base_file = YamlFile(self.github_file, self.mock_git)

    def test_save_options(self):
        self.base_file.save("Test message", False, {"explicit_start": False})
        self.mock_git.update_file.assert_called_once_with(
            self.github_file, "test:\n  foo: bar\n  iam: blah\n", "Test message", False
        )

    def test_save_default_options(self):
        self.base_file.save("Test message", False)
        self.mock_git.update_file.assert_called_once_with(
            self.github_file,
            "---\ntest:\n  foo: bar\n  iam: blah\n",
            "Test message",
            False,
        )
