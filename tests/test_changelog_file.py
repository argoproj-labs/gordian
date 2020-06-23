import unittest
from unittest.mock import MagicMock, patch
from gordian.repo import Repo
from gordian.files import ChangelogFile
from .utils import Utils
from datetime import datetime

class TestBaseFile(unittest.TestCase):

    def setUp(self):
        self.github_file = Utils.create_github_content_file(file='changelog_no_footer.md')
        self.mock_git = MagicMock()
        self.repo = Repo('test', github=self.mock_git)
        self.repo.new_version = '1.2.0'
        self.changelog = ChangelogFile(self.github_file, self.repo)

    def test_iterable(self):
        assert(iter(self.changelog))

    def test_assert_added(self):
        self.changelog.added('test')
        assert(len(self.changelog._added) == 1)
        assert(self.changelog._added[0] == ('test', None))

    def test_assert_added_with_ticket(self):
        self.changelog.added('test', 'something-1234')
        assert(len(self.changelog._added) == 1)
        assert(self.changelog._added[0] == ('test', 'something-1234'))

    def test_assert_updated(self):
        self.changelog.updated('test')
        assert(len(self.changelog._updated) == 1)
        assert(self.changelog._updated[0] == ('test', None))

    def test_assert_removed(self):
        self.changelog.removed('test')
        assert(len(self.changelog._removed) == 1)
        assert(self.changelog._removed[0] == ('test', None))

    def test_save_changelog(self):
        self.changelog.added('test')
        self.changelog.save('save file', False)

    def test_changelog_format_no_footer(self):
        changelog = '''# Changelog

## [1.2.0] - 2020-06-02
### Added
- something
### Removed
- something else [ticket-1234]

## [1.1.0] - 2020-02-15
### Added
- Something new JIRA-10000
- Something else SRE-11000

## [1.0.0] - 2020-02-14
### Changed
- Foobar SRE-9999
### Removed
- SRE-8454 Removed a feature

'''
        self.changelog.added('something')
        self.changelog.removed('something else', 'ticket-1234')
        with patch('gordian.files.changelog_file.ChangelogFile._format_date', return_value=datetime(2020, 6, 2).strftime('%Y-%m-%d')):
            assert(self.changelog._dump() == changelog)

    def test_changelog_format_with_footer(self):
        self.github_file = Utils.create_github_content_file(file='changelog_with_footer.md')
        self.changelog = ChangelogFile(self.github_file, self.repo)
        changelog = '''# Changelog

## [1.2.0] - 2020-06-02
### Added
- something
### Removed
- something else [ticket-1234]

## [1.1.0] - 2020-02-15
### Added
- Something new JIRA-10000
- Something else SRE-11000

## [1.0.0] - 2020-02-14
### Changed
- Foobar SRE-9999
### Removed
- SRE-8454 Removed a feature

this is a footer'''
        self.changelog.added('something')
        self.changelog.removed('something else', 'ticket-1234')
        with patch('gordian.files.changelog_file.ChangelogFile._format_date', return_value=datetime(2020, 6, 2).strftime('%Y-%m-%d')):
            assert(self.changelog._dump() == changelog)
