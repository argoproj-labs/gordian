from github import Github
from github import GithubException
import datetime
import logging
import os
from gordian.files import YamlFile, JsonFile

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.github.com'


class Repo:

    def __init__(self, repo_name, github_api_url=None, branch=None, git=None, files=[]):
        if github_api_url is None:
            self.github_api_url = BASE_URL
        else:
            self.github_api_url = github_api_url

        if git is None:
            if "GIT_TOKEN" in os.environ:
                git = Github(base_url=self.github_api_url, login_or_token=os.environ['GIT_TOKEN'])
            else:
                git = Github(base_url=self.github_api_url, login_or_token=os.environ['GIT_USERNAME'], password=os.environ['GIT_PASSWORD'])

        self.repo_name = repo_name
        self._repo = git.get_repo(repo_name)
        self.files = files
        self.version_file = None
        self.branch_exists = False
        self.dirty = False

        if branch:
            self.branch_name = f"refs/heads/{branch}"
        else:
            self.branch_name = f"refs/heads/{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S.%f')}"

    def get_objects(self, filename, klass=None):
        file = self.find_file(filename)

        if file is None:
            raise FileNotFoundError

        if klass:
            return klass(file, self)

        _, ext = os.path.splitext(filename)

        if ext in ('.yaml', '.yml'):
            return YamlFile(file, self)
        if ext in ('.json'):
            return JsonFile(file, self)

    def get_files(self):
        if not self.files:
            contents = self._repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.path == 'version':
                    self.version_file = file_content
                if file_content.type == 'dir':
                    contents.extend(self._repo.get_contents(file_content.path))
                else:
                    self.files.append(file_content)

        return self.files

    def find_file(self, filename):
        for file in self.get_files():
            if file.path == filename:
                return file

    def make_branch(self):
        sb = self._repo.get_branch('master')
        try:
            ref = self._repo.create_git_ref(ref=self.branch_name, sha=sb.commit.sha)
        except GithubException as e:
            print(f"Branch {self.branch_name} already exists in github")
        self.branch_exists = True

    def bump_version(self, bump_major, bump_minor, bump_patch, dry_run=False):
        if not bump_major and not bump_minor and not bump_patch:
            return
        if self.version_file is None:
            logger.info('There is no version file in the repository, skipping bumping')
            return

        version = self.version_file.decoded_content.decode('utf-8')
        major, minor, patch = version.split('.')
        if bump_major:
            major = str(int(major) + 1)
            minor = patch = '0'
        elif bump_minor:
            minor = str(int(minor) + 1)
            patch = '0'
        elif bump_patch:
            patch = str(int(patch) + 1)
        new_version = '.'.join([major, minor, patch])
        logger.info(f'Bumping version {new_version}')
        self.update_file(
            self.version_file,
            new_version,
            'Bumping version',
            dry_run
        )

    def update_file(self, repo_file, content, message, dry_run=False):
        self.dirty = True
        logger.info(message)
        if dry_run:
            logger.info('dry-run')
            return

        if not self.branch_exists:
            self.make_branch()

        self._repo.update_file(
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
            self.make_branch()

        self._repo.create_file(
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
            self.make_branch()

        self._repo.delete_file(
            file.path,
            message,
            file.sha,
            branch=self.branch_name
        )
