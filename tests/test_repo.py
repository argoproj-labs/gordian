import unittest
import pytest
from gordian.repo import Repo
from unittest.mock import MagicMock, patch, call
from gordian.files import YamlFile
from .utils import Utils

class TestRepo(unittest.TestCase):

    @patch('gordian.repo.Github')
    def setUp(self, mock_git):
        self.mock_git = MagicMock()
        self.mock_repo = MagicMock()
        self.mock_branches = MagicMock()
        self.repo = Repo('test', git=self.mock_git)
        self.repo.files.append(Utils.create_github_content_file())

        self.mock_repo.get_branches.return_value = self.mock_branches
        mock_git.get_repo.return_value = self.mock_repo
        self.instance = Repo(None, branch='', git=mock_git)

    def test_make_branch(self):
        self.instance.branch_exists = False
        mock_branch = MagicMock()
        self.mock_repo.get_branch.return_value = mock_branch
        mock_branch.commit.sha = "5e69ff00a3be0a76b13356c6ff42af79ff469ef3"
        self.instance.make_branch()
        self.assertTrue(self.instance.branch_exists)
        self.mock_repo.get_branch.assert_called_once_with('master')
        self.mock_repo.create_git_ref.assert_called_once()

    def test_default_github_url(self):
        self.assertEqual(self.repo.github_api_url, 'https://api.github.com')

    def test_override_github_url(self):
        repo = Repo('test', github_api_url='https://test.github.com', git=self.mock_git)
        self.assertEqual(repo.github_api_url, 'https://test.github.com')

    def test_get_object_does_not_exist(self):
        with pytest.raises(FileNotFoundError):
            self.repo.get_objects('test')

    def test_get_existing_object(self):
        contents = self.repo.get_objects('/content.yaml')
        assert(isinstance(contents, YamlFile))
        
    def test_new_files_object(self):
        self.assertEquals(len(self.repo.files), 1)
        repo_two = Repo('test_two', github_api_url='https://test.github.com', git=self.mock_git)
        self.assertEquals(len(repo_two.files), 0)
        
    def test_get_files(self):
        self.repo.set_target_branch('target')
        self.repo.files = []
        self.repo._repo = MagicMock()
        repository_file = MagicMock(path='afile.txt', type='not_dir')
        self.repo._repo.get_contents.side_effect = [[MagicMock(path='directory', type='dir')],[repository_file]]
        self.repo.get_files()
        self.repo._repo.get_contents.assert_has_calls([call('', 'refs/heads/target'), call('directory', 'refs/heads/target')])
        self.assertEquals(self.repo.files, [repository_file])

    def test_set_target_branch(self):
        cached_files = ['cached_file', 'cached_file', 'cached_file']
        self.repo.files = cached_files.copy()
        self.repo.set_target_branch('master')
        self.assertEqual(self.repo.files, cached_files)

        self.repo.set_target_branch('Something different')
        self.assertEqual(self.repo.files, [])
        self.assertEqual(self.repo.target_branch, 'Something different')
        self.assertEqual(self.repo.target_ref, 'refs/heads/Something different')
