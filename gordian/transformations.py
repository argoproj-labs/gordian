import logging
import yaml
import re
import jsonpatch
import copy
from deepdiff import DeepDiff

logger = logging.getLogger(__name__)


class Transformation(object):

    def __init__(self, args, repo):
        self.args = args
        self.repo = repo
        self.dry_run = args.dry_run

    def run(self):
        raise NotImplementedError('Please subclass the transformation and overrite this method')


class SearchAndReplace(Transformation):

    def __init__(self, args, repo):
        super().__init__(args, repo)
        self.changesets = zip(args.search, args.replace)

    def is_word_found(self, file, search):
        return search in str(file)

    def run(self):
        changes = False
        for search, replace in self.changesets:
            for file in self.repo.get_files():
                file_str = file.decoded_content
                if not self.is_word_found(file_str, search):
                    logger.debug(f"Ignoring {file}")
                    continue
                file_str = file_str.replace(search.encode(), replace.encode())
                changes = True

                message = f"Replacing '{search}' with '{replace}' in {file}"
                self.repo.update_file(file, file_str, message, self.dry_run)
        return changes


class JsonPatch(Transformation):

    def __init__(self, args, repo):
        super().__init__(args, repo)
        self.patch_path = args.patch_path
        self.file_regexp = args.file_regexp
        self.patch = jsonpatch.JsonPatch.from_string(open(self.patch_path, 'r').read())

    def run(self):
        changes = False
        for f in self.repo.get_files():
            file_changes = False
            if not re.match(self.file_regexp, f.path):
                continue
            logger.info(f'Path name: {f.path}')
            k8s_patches = list(yaml.safe_load_all(f.decoded_content))
            for r in k8s_patches:
                original = copy.deepcopy(r)
                try:
                    self.patch.apply(r, in_place=True)
                except jsonpatch.JsonPointerException as e:
                    logger.debug(e)
                except jsonpatch.JsonPatchTestFailed as e:
                    logger.debug(e)
                diff = DeepDiff(r, original)
                if diff != {}:
                    logger.info(f'Detected changes: {diff}')
                    message = f'Applied json patch defined in {self.patch_path}'
                    file_changes = True
            if file_changes:
                changes = True
                file_str = yaml.dump_all(k8s_patches, default_flow_style=False, explicit_start=True)
                logger.debug(file_str)
                self.repo.update_file(f, file_str, message, self.dry_run)
        return changes
