import unittest
import pytest
import os
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
        self.repo = Repo('test', github=self.mock_git)
        self.repo.files.append(Utils.create_github_content_file())

        self.mock_repo.get_branches.return_value = self.mock_branches
        self.mock_git.get_repo.return_value = self.mock_repo

    @patch('gordian.repo.Github')
    def test_remove_dot_git_from_repo_name(self, mock_git):
        self.mock_git.reset_mock()
        self.repo = Repo('test.git', github=self.mock_git)
        self.mock_git.get_repo.assert_called_once_with('test')

    def test_no_fork(self):
        repo = Repo('test_repo', branch='', github=self.mock_git, fork=False)
        repo._target_repo.create_fork.assert_not_called()
        self.assertEqual(repo._source_repo, repo._target_repo)

    def test_fork(self):
        repo = Repo('test_repo', branch='', github=self.mock_git, fork=True)
        repo._target_repo.create_fork.assert_called_once()
        self.assertNotEqual(repo._source_repo, repo._target_repo)

    def test_make_branch_fork(self):
        repo = Repo('test_repo', branch='', github=self.mock_git, fork=True)
        repo.branch_exists = False
        mock_branch = MagicMock()
        self.mock_repo.get_branch.return_value = mock_branch
        mock_branch.commit.sha = "5e69ff00a3be0a76b13356c6ff42af79ff469ef3"
        repo._make_branch()
        self.assertTrue(repo.branch_exists)
        repo._source_repo.get_branch.assert_called_once_with('master')
        repo._source_repo.create_git_ref.assert_called_once()

    def test_make_branch_no_fork(self):
        repo = Repo('test_repo', branch='', github=self.mock_git, fork=False)
        repo.branch_exists = False
        mock_branch = MagicMock()
        self.mock_repo.get_branch.return_value = mock_branch
        mock_branch.commit.sha = "5e69ff00a3be0a76b13356c6ff42af79ff469ef3"
        repo._make_branch()
        self.assertTrue(repo.branch_exists)
        repo._source_repo.get_branch.assert_called_once_with('master')
        repo._source_repo.create_git_ref.assert_called_once()

    def test_default_github_url(self):
        self.assertEqual(self.repo.github_api_url, 'https://api.github.com')

    def test_override_github_url(self):
        repo = Repo('test', github_api_url='https://test.github.com', github=self.mock_git)
        self.assertEqual(repo.github_api_url, 'https://test.github.com')

    def test_get_object_does_not_exist(self):
        with pytest.raises(FileNotFoundError):
            self.repo.get_objects('test')

    def test_get_existing_object(self):
        contents = self.repo.get_objects('/content.yaml')
        assert(isinstance(contents, YamlFile))

    def test_new_files_object(self):
        self.assertEquals(len(self.repo.files), 1)
        repo_two = Repo('test_two', github_api_url='https://test.github.com', github=MagicMock())
        self.assertEquals(len(repo_two.files), 0)

    def test_get_files(self):
        self.repo._set_target_branch('target')
        self.repo.files = []
        self.repo._source_repo = MagicMock()
        repository_file = MagicMock(path='afile.txt', type='not_dir')
        self.repo._source_repo.get_contents.side_effect = [[MagicMock(path='directory', type='dir')],[repository_file]]
        self.repo.get_files()
        self.repo._source_repo.get_contents.assert_has_calls([call('', 'target'), call('directory', 'target')])
        self.assertEquals(self.repo.files, [repository_file])

    def test_set_target_branch(self):
        self.repo._set_target_branch('master')
        self.assertEqual(self.repo.source_branch, 'refs/heads/master')

    def test_set_target_branch_source_branch(self):
        self.repo._set_target_branch('master', 'something')
        self.assertEqual(self.repo.source_branch, 'refs/heads/something')

    def test_set_target_branch_reset_file_cache(self):
        self.repo._set_target_branch('master')
        cached_files = ['cached_file', 'cached_file', 'cached_file']
        self.repo.files = cached_files
        self.assertEqual(self.repo.files, cached_files)

        self.repo._set_target_branch('Something different')
        self.assertEqual(self.repo.files, [])
        self.assertEqual(self.repo.target_branch, 'Something different')
        self.assertEqual(self.repo.target_ref, 'refs/heads/Something different')

    def test_create_pr(self):
        repo = Repo('test_repo', branch='', github=self.mock_git)
        repo._target_repo = MagicMock()
        repo._source_repo = MagicMock()
        repo._source_repo.owner.login = 'someone'
        repo.branch_name = 'branch'
        pr = repo.create_pr('test', '', 'target_branch', ['test'])
        repo._target_repo.create_pull.assert_called_once_with('test', '', 'target_branch', 'someone:branch')
        pr.set_labels.assert_called_once_with('test')
        repo._source_repo.create_pull.assert_not_called()

    def test_create_pr_no_labels(self):
        repo = Repo('test_repo', branch='', github=self.mock_git)
        repo._target_repo = MagicMock()
        repo._source_repo = MagicMock()
        repo._source_repo.owner.login = 'someone'
        repo.branch_name = 'branch'
        pr = repo.create_pr('test', '', 'target_branch')
        repo._target_repo.create_pull.assert_called_once_with('test', '', 'target_branch', 'someone:branch')
        pr.set_labels.assert_not_called()
        repo._source_repo.create_pull.assert_not_called()

    def test_get_new_version_major(self):
        version_file = MagicMock()
        version_file.decoded_content = '1.2.3'.encode('utf-8')
        self.repo.version_file = version_file
        self.repo.semver_label = 'major'
        self.repo._get_new_version()
        self.assertEqual(self.repo.new_version, '2.0.0')

    def test_get_new_version_minor(self):
        version_file = MagicMock()
        version_file.decoded_content = '1.2.3'.encode('utf-8')
        self.repo.version_file = version_file
        self.repo.semver_label = 'minor'
        self.repo._get_new_version()
        self.assertEqual(self.repo.new_version, '1.3.0')

    def test_get_new_version_patch(self):
        version_file = MagicMock()
        version_file.decoded_content = '1.2.3'.encode('utf-8')
        self.repo.version_file = version_file
        self.repo.semver_label = 'patch'
        self.repo._get_new_version()
        self.assertEqual(self.repo.new_version, '1.2.4')

    @patch('gordian.repo.Github')
    def test_init_with_passed_token(self, mock_git):
        Repo('test_repo', token='abcdef')
        args = {'login_or_token': 'abcdef', 'base_url': 'https://api.github.com'}
        mock_git.assert_called_with(**args)

    @patch.dict(os.environ, {'GIT_TOKEN': '12345'})
    @patch('gordian.repo.Github')
    def test_init_with_token_from_env(self, mock_git):
        Repo('test_repo')
        args = {'login_or_token': '12345', 'base_url': 'https://api.github.com'}

        mock_git.assert_called_with(**args)

    @patch.dict(os.environ, {'GIT_USERNAME': 'test-user', 'GIT_PASSWORD': 'test-pass'})
    @patch('gordian.repo.Github')
    def test_init_with_user_pass_env(self, mock_git):
        Repo('test_repo')
        args = {'login_or_token':'test-user', 'password':'test-pass', 'base_url': 'https://api.github.com'}

        mock_git.assert_called_with(**args)

    @patch('gordian.repo.Github')
    def test_create_file(self, mock_git):
        repo = Repo('test_repo', github=mock_git)
        repo.create_file('test', 'test', 'test file create')

        repo._source_repo.create_file.assert_called_once()
        self.assertTrue(repo.dirty)

    @patch('gordian.repo.Github')
    def test_delete_file(self, mock_git):
        mock_file = MagicMock()
        repo = Repo('test_repo', github=mock_git)
        repo.delete_file(mock_file, 'test file delete')

        repo._source_repo.delete_file.assert_called_once()
        self.assertTrue(repo.dirty)

    def test_get_files_with_path(self):
        self.repo._set_target_branch('target')
        self.repo.files = []
        self.repo._source_repo = MagicMock()
        repository_file = MagicMock(path='test/afile.txt', type='not_dir')
        self.repo._source_repo.get_contents.side_effect = [[MagicMock(path='directory', type='dir')],[repository_file]]
        self.repo.get_files('test')
        self.repo._source_repo.get_contents.assert_has_calls([call('test', 'target'), call('directory', 'target')])
        self.assertEquals(self.repo.files, [repository_file])

    def test__get_github_client(self):
        repo = Repo('test_repo', branch='', github=self.mock_git)

        self.assertIsNotNone(repo.get_github_client())
        self.assertEqual(repo.get_github_client(), self.mock_git)
