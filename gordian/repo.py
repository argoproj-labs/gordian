from github import Github
from github import GithubException
import datetime
import logging
import os
import sys
import time
from retry import retry
from gordian.files import *

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.github.com'


class Repo:

    def __init__(self, repo_name, github_api_url=None, branch=None, github=None, files=None, semver_label=None, target_branch='master', fork=False):
        if github_api_url is None:
            self.github_api_url = BASE_URL
        else:
            self.github_api_url = github_api_url

        if github is not None:
            self._github = github
        else:
            if "GIT_TOKEN" in os.environ:
                logger.debug('Using git token')
                self._github = Github(base_url=self.github_api_url, login_or_token=os.environ['GIT_TOKEN'])
            else:
                logger.debug('Using git username and password')
                self._github = Github(base_url=self.github_api_url, login_or_token=os.environ['GIT_USERNAME'], password=os.environ['GIT_PASSWORD'])

        if files is None:
            files = []
        self.files = files

        self._initialize_repos(repo_name, fork)

        self.version_file = None
        self.changelog_file = None
        self.branch_exists = False
        self.dirty = False
        self.new_version = None
        self.semver_label = semver_label
        self._set_target_branch(target_branch, branch)

        logger.debug(f'Github API: {self.github_api_url}')
        logger.debug(f'Repo name: {repo_name}')

    def get_objects(self, filename, klass=None):
        file = self.find_file(filename)

        if filename == 'CHANGELOG.md':
            return self.changelog

        if file is None:
            raise FileNotFoundError

        if klass:
            return klass(file, self)

        _, ext = os.path.splitext(filename)

        if ext in ('.yaml', '.yml'):
            return YamlFile(file, self)
        if ext == '.json':
            return JsonFile(file, self)
        if ext == '.md':
            return MarkdownFile(file, self)

    def get_files(self):
        if not self.files:
            contents = self._get_repo_contents('')

            while contents:
                file = contents.pop(0)
                if file.path == 'version':
                    self.version_file = file
                elif file.path == 'CHANGELOG.md':
                    self.changelog = ChangelogFile(file, self)
                elif file.type == 'dir':
                    contents.extend(self._get_repo_contents(file.path))
                else:
                    self.files.append(file)

        self._get_new_version()

        return self.files

    def find_file(self, filename):
        for file in self.get_files():
            if file.path == filename:
                return file

    def _initialize_repos(self, repo_name, fork):
        self._target_repo = self._github.get_repo(repo_name)
        if fork:
            logger.info('Forking repo...')
            self._source_repo = self._target_repo.create_fork()
        else:
            self._source_repo = self._target_repo

    def _set_target_branch(self, target_branch, source_branch=None):
        logger.debug(f'Target branch: {target_branch}')
        logger.debug(f'Source branch: {source_branch}')

        # Resetting the file cache when we change the branch
        self.files = []

        self.target_branch = target_branch
        self.target_ref = f"refs/heads/{self.target_branch}"

        if source_branch:
            self.branch_name = f"refs/heads/{source_branch}"
            self.source_branch = self.branch_name
        else:
            self.branch_name = f"refs/heads/{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S.%f')}"
            self.source_branch = self.target_ref

    @retry(GithubException, tries=3, delay=1, backoff=2)
    def _get_repo_contents(self, path):
        try:
            logger.debug(f'Fetching repo contents {path}...')
            return self._source_repo.get_contents(path, self.source_branch)
        except GithubException as e:
            if e.status == 404:
                raise e
            logger.info(f'Error fetching repo contents: {e}')

    @retry(GithubException, tries=3, delay=1, backoff=2)
    def _make_branch(self):
        branch = self._get_branch()
        logger.debug(f'Creating branch {self.branch_name}')

        try:
            ref = self._source_repo.create_git_ref(ref=self.branch_name, sha=branch.commit.sha)
        except GithubException as e:
            logger.debug(f'Branch {self.branch_name} already exists in github')
        self.branch_exists = True

    def _get_branch(self):
        logger.debug(f'Fetching branch {self.target_branch}...')
        return self._source_repo.get_branch(self.target_branch)

    def bump_version(self, dry_run=False):
        if self.new_version is None:
            return

        logger.info(f'Bumping version {self.new_version}')
        self.update_file(
            self.version_file,
            self.new_version,
            f'Bumping version to {self.new_version}',
            dry_run
        )

    def update_file(self, repo_file, content, message, dry_run=False):
        self.dirty = True
        logger.info(message)
        if dry_run:
            logger.info('dry-run')
            return

        if not self.branch_exists:
            self._make_branch()

        logger.debug(f'Updating file {repo_file.path}')
        self._source_repo.update_file(
            repo_file.path,
            message,
            content,
            repo_file.sha,
            branch=self.branch_name
        )

    def create_file(self, path, contents, message, dry_run=False):
        self.dirty = True
        logger.info(message)
        if dry_run:
            logger.info('dry-run')
            return

        if not self.branch_exists:
            self._make_branch()

        logger.debug(f'Creating file {path}')
        self._source_repo.create_file(
            path,
            message,
            contents,
            branch=self.branch_name
        )

    def delete_file(self, file, message, dry_run=False):
        self.dirty = True
        logger.info(message)
        if dry_run:
            logger.info('dry-run')
            return

        if not self.branch_exists:
            self._make_branch()

        logger.debug(f'Deleting file {file.path}')
        self._source_repo.delete_file(
            file.path,
            message,
            file.sha,
            branch=self.branch_name
        )

    def create_pr(self, pr_message, pr_body, target_branch, labels=[]):
        pr = self._target_repo.create_pull(
            pr_message,
            pr_body,
            target_branch,
            f'{self._source_repo.owner.login}:{self.branch_name}'
        )
        if labels:
            pr.set_labels(*labels)
        return pr

    def _get_new_version(self):
        if self.semver_label is None:
            return

        if self.version_file is None:
            logger.info('There is no version file in the repository, skipping bumping')
            return

        version = self.version_file.decoded_content.decode('utf-8')
        major, minor, patch = version.split('.')
        if self.semver_label == 'major':
            major = str(int(major) + 1)
            minor = patch = '0'
        elif self.semver_label == 'minor':
            minor = str(int(minor) + 1)
            patch = '0'
        elif self.semver_label == 'patch':
            patch = str(int(patch) + 1)
        self.new_version = '.'.join([major, minor, patch])
