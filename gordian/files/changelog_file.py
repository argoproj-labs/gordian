from . import MarkdownFile
import re
from datetime import datetime

CHANGELOG_ENTRY_REGEX = '.*\[([0-9]*\.[0-9]*\.[0-9]*)\] - [0-9]{4}-[0-9]{1,2}-[0-9]+'

class ChangelogFile(MarkdownFile):

    def __init__(self, github_file, repo):
        self.changelog_entry_types = [ 'added', 'updated', 'removed' ]
        self._generate_interface_methods()
        super().__init__(github_file, repo)

    def _load_objects(self):
        string_lines = [line.decode('utf-8') for line in super()._load_objects()]
        self.header = []
        changelog_entries = []
        changelog_entry_block = []
        empty_previous_line = False
        inside_changelog_entry_block = False
        footer_start = None

        for i, line in enumerate(string_lines):
            # set on previous iteration
            if empty_previous_line:
                if re.search(CHANGELOG_ENTRY_REGEX, line):

                    # reached the end of the header (start of the changelog)
                    if not self.header:
                        self.header = string_lines[0:i]

                    # reached end of previous block (start of next changelog entry)
                    if changelog_entry_block:
                        changelog_entries.append(changelog_entry_block)

                    inside_changelog_entry_block = True
                    changelog_entry_block = []

                # if previous line was empty and it did _not_ match the changelog entry regex,
                # it means the end of the changelog entries was reached, and now it's reading
                # through the footer.
                else:
                    inside_changelog_entry_block = False
                    footer_start = i

            if inside_changelog_entry_block:
                changelog_entry_block.append(line)

            # used for the subsequent iteration to determine when we've gone through all
            # the changelog entries
            empty_previous_line = not line

        changelog_entries.append(changelog_entry_block)
        if footer_start:
            self.footer = string_lines[footer_start:len(string_lines) - 1]
        else:
            self.footer =  []

        return changelog_entries

    def _dump(self):
        blocks = []
        for o in self.objects:
            blocks.append('\n'.join(o))

        entries = self._format_new_changelog_entry()

        lines = ['\n'.join(self.header)]
        if entries:
            lines.append('\n'.join(entries))
            lines.append('')
        lines.append('\n'.join(blocks))
        lines.append('\n'.join(self.footer))

        return '\n'.join(lines)

    def _format_new_changelog_entry(self):
        lines = []
        for changelog_entry_type in self.changelog_entry_types:
            lines += self._format_list_entry(changelog_entry_type)

        if lines:
            header = f"## [{self.repo.new_version}] - {self._format_date()}"
            lines.insert(0, header)
        return lines

    def _format_list_entry(self, list_type):
        lines = []
        entries = getattr(self, f'_{list_type}')
        for entry, ticket in entries:
            if ticket:
                line = f'{entry} [{ticket}]'
            else:
                line = entry
            lines.append(f'- {line}')

        if lines:
            header = f'### {list_type.capitalize()}'
            lines.insert(0, header)
        return lines

    def _generate_interface_methods(self):
        for changelog_entry_type in self.changelog_entry_types:
            internal_store = f'_{changelog_entry_type}'

            def fn(self, entry, ticket=None, store=internal_store):
                getattr(self, store).append((entry, ticket))

            setattr(ChangelogFile, changelog_entry_type, fn)
            setattr(ChangelogFile, internal_store, [])

    def _format_date(self):
        return datetime.now().strftime('%Y-%m-%d')
