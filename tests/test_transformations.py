import unittest

from gordian.files.plaintext_file import PlainTextFile
from gordian.repo import Repo
from gordian.transformations import SearchAndReplace, PlainTextUpdater
from unittest.mock import MagicMock, patch

from tests.utils import Utils


class TestSearchAndReplaceTransformation(unittest.TestCase):

    class Args(object):
        def __init__(self, dry_run=False, search=['iam'], replace=['hello'], file='content.txt'):
            self.dry_run = dry_run
            self.search = search
            self.replace = replace
            self.file = file

    @patch('gordian.repo.Github')
    def setUp(self, mock_git):
        self.mock_repo = MagicMock()
        self.mock_branches = MagicMock()
        self.mock_repo.get_branches.return_value = self.mock_branches
        mock_git.get_repo.return_value = self.mock_repo
        self.mock_repo.get_contents.return_value = []
        self.instance = Repo('test_repo', branch='', github=mock_git, files=[])
        self.instance.branch_exists = False
        f = open('./tests/fixtures/content.yaml', 'r')
        contents = f.read()
        mock_file = MagicMock()
        mock_file.decoded_content = contents.encode()
        self.instance.files.append(mock_file)
        self.sandr = SearchAndReplace(TestSearchAndReplaceTransformation.Args(), self.instance)

    def test_both_false_update_files(self):
        assert(self.sandr.run())
        self.instance._source_repo.create_git_ref.assert_called_once()
        self.instance._source_repo.update_file.assert_called_once()

    def test_is_word_found(self):
        f = open('./tests/fixtures/content.yaml', 'r')
        contents = f.read()
        self.assertTrue(self.sandr.is_word_found(contents, 'iam'))
        self.assertFalse(self.sandr.is_word_found(contents, 'hello'))

    def test_pr_false_update_files(self):
        source_repo = MagicMock()
        self.instance._source_repo = source_repo
        self.instance.branch_exists = True
        assert(self.sandr.run())
        source_repo.update_file.assert_called_once()

    def test_update_files_none(self):
        self.sandr.changesets = (('hello', 'iam'),)
        self.sandr.run()
        self.mock_repo.update_file.assert_not_called()
        self.mock_repo.create_pull.assert_not_called()

    def test_update_files_empty(self):
        self.instance.files = []
        self.sandr.run()
        self.mock_repo.update_file.assert_not_called()
        self.mock_repo.create_pull.assert_not_called()

    def test_PlainTextUpdater(self):
        self.file = Utils.create_github_content_file(file='content.txt')
        self.ptf = PlainTextFile(self.file, self.instance)
        self.instance.files = [self.ptf.github_file]
        self.ptu = PlainTextUpdater(TestSearchAndReplaceTransformation.Args(), self.instance)
        self.assertIs(self.ptu.run(), True)
