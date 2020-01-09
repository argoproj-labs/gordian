import unittest
from gordian.repo import Repo
from unittest.mock import MagicMock, patch


class TestRepo(unittest.TestCase):

    @patch('gordian.repo.Github')
    def setUp(self, mock_git):
        self.mock_git = MagicMock()
        self.mock_repo = MagicMock()
        self.mock_branches = MagicMock()
        self.repo = Repo('test', git=self.mock_git)
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
        self.mock_repo.get_branch.assert_called_once()
        self.mock_repo.create_git_ref.assert_called_once()

    def test_default_github_url(self):
        self.assertEqual(self.repo.github_api_url, 'https://api.github.com')

    def test_override_github_url(self):
        self.repo = Repo('test', github_api_url='https://test.github.com', git=self.mock_git)
        self.assertEqual(self.repo.github_api_url, 'https://test.github.com')
