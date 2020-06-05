import logging
import sys
import re
import math
from gordian.gordian import get_basic_parser, apply_transformations
from gordian.config import Config
from gordian.transformations import Transformation
from gordian.repo import Repo

logger = logging.getLogger(__name__)


class NullTest(Transformation):

    def __init__(self, args, repo):
        super().__init__(args, repo)
        self.environments = args.environments

    def run(self):
        file = self.repo.get_objects('service/global-values.yaml')

        for obj in file:
            if obj['kind'] != 'Deployment':
                continue

            for container in obj['spec']['template']['spec']['containers']:
                if container['name'] != 'service-container':
                    continue

                container['resources']['limits']['cpu'] = None

        file.save('Remove CPU limit', self.dry_run)

        self.repo.changelog.added('added a test', 'SRE-1234')
        self.repo.changelog.updated('updated something')
        self.repo.changelog.removed('removed something', 'SRE-6245')
        self.repo.changelog.save('test', self.dry_run)

def main():
    parser = get_basic_parser()
    parser.add_argument(
        '-e', '--environments',
        required=False,
        dest='environments',
        default='prd-.*',
        help='Environments to update.'
    )
    args = parser.parse_args(sys.argv[1:])
    apply_transformations(args, [NullTest])

if __name__ == '__main__':
    main()
