import unittest
from gordian.config import Config
from gordian.gordian import apply_transformations
from unittest.mock import MagicMock, patch, call, Mock, mock_open, ANY


class TestGordian(unittest.TestCase):

    class Args(object):
        def __init__(self, config_file='./tests/fixtures/test_config.yaml', dry_run = False):
            self.config_file = config_file
            self.major = False
            self.minor = False
            self.patch = False
            self.dry_run = dry_run
            self.pr_message = 'test'
            self.branch = 'test'
            self.github_api = None
            self.semver_label = None
            self.target_branch = 'master'
            self.pr_labels = ['test']
            self.description = ''
            self.description_file = None
            self.fork = False

    def test_apply_transformations_without_changes(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation') as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = False
            apply_transformations(TestGordian.Args(), [TransformationMockClass])
            RepoMock.assert_has_calls([
                call('testOrg/TestService1', github_api_url=None, branch='test', semver_label=None, target_branch='master', fork=False),
                call('testOrg/TestService2', github_api_url=None, branch='test', semver_label=None, target_branch='master', fork=False)
            ])

    def test_apply_transformations_with_changes(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation') as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            apply_transformations(TestGordian.Args(), [TransformationMockClass])
            RepoMock.assert_has_calls([call().bump_version(False), call().bump_version(False)], any_order=True)
            RepoMock.assert_has_calls([call().create_pr('test', '', 'master', ANY), call().create_pr('test', '', 'master', ANY)], any_order=True)

    def test_apply_transformations_with_changes_dry_run(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation') as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            apply_transformations(TestGordian.Args(dry_run=True), [TransformationMockClass])
            RepoMock.assert_has_calls([call().bump_version(True), call().bump_version(True)], any_order=True)
            self.assertNotIn(call().repo.create_pr('test', '', 'master', ANY), RepoMock.mock_calls)

    def test_apply_transformations_with_changes_and_callback(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation') as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            callback_mock = MagicMock()
            args = TestGordian.Args()
            args.target_branch = 'target_branch'
            apply_transformations(args, [TransformationMockClass], callback_mock)
            pull_request = RepoMock.return_value.create_pr.return_value
            RepoMock.assert_has_calls([call().bump_version(False), call().bump_version(False)], any_order=True)
            RepoMock.assert_has_calls([
                call().create_pr('test', '', 'target_branch', ANY),
                call().create_pr('test', '', 'target_branch', ANY)],
                any_order=True
            )
            callback_mock.assert_has_calls([
                call('testOrg/TestService1', pull_request),
                call('testOrg/TestService2', pull_request)]
            )

    def test_apply_transformations_with_changes_default_labels(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation', ) as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            gordian_args = TestGordian.Args()
            gordian_args.pr_labels = []
            apply_transformations(gordian_args, [TransformationMockClass])
            RepoMock.assert_has_calls([call().bump_version(False), call().bump_version(False)], any_order=True)
            RepoMock.assert_has_calls([call().create_pr('test', '', 'master', ANY), call().create_pr('test', '', 'master', ANY)], any_order=True)
            self.assertNotIn(call()._repo.create_pull().set_labels(ANY), RepoMock.mock_calls)

    def test_apply_transformations_with_changes_custom_description(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation', ) as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            gordian_args = TestGordian.Args()
            description = 'Custom file for pr description\n'
            gordian_args.description_file = './tests/fixtures/pr_description'
            apply_transformations(gordian_args, [TransformationMockClass])
            RepoMock.assert_has_calls([call().bump_version(False), call().bump_version(False)], any_order=True)
            RepoMock.assert_has_calls([call().create_pr('test', description, 'master', ANY), call().create_pr('test', description, 'master', ANY)], any_order=True)
