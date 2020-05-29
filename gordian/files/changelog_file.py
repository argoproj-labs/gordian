from . import MarkdownFile
import re

ENTRY_REGEX = '.*\[([0-9]*\.[0-9]*\.[0-9]*)\] - [0-9]{4}-[0-9]{1,2}-[0-9]+'

class ChangelogFile(MarkdownFile):

    def __init__(self, github_file, repo):
        self.header = []
        super().__init__(github_file, repo)

    def _load_objects(self):
        string_lines = [line.decode('utf-8') for line in super()._load_objects()]
        changelog_entries = []
        changelog_entry_block = []
        empty_previous_line = False
        inside_changelog_entry_block = False
        footer_start = 0

        for i, line in enumerate(string_lines):
            # set on previous iteration
            if empty_previous_line:
                if re.search(ENTRY_REGEX, line):
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
        self.footer = string_lines[footer_start:len(string_lines) - 1]

        return changelog_entries

    def _dump(self):
        blocks = []
        for o in self.objects:
            blocks.append('\n'.join(o))

        return '\n'.join(
            [
                '\n'.join(self.header),
                '\n'.join(blocks),
                '\n'.join(self.footer)
            ]
        )
