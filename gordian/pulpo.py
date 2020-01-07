import logging
import sys
from .gordian import get_basic_parser, apply_transformations
from .config import Config
from .transformations import JsonPatch
from .repo import Repo

logger = logging.getLogger(__name__)


def main():
    parser = get_basic_parser()
    parser.add_argument(
        dest='patch_path',
        help='Path to the json patch file.'
    )
    parser.add_argument(
        '-f', '--filter',
        required=False,
        default='.*\.yaml',
        dest='file_regexp',
        help='This regular expression will be used to filter the files to apply the transformation.'
    )
    args = parser.parse_args(sys.argv[1:])
    apply_transformations(args, [JsonPatch])


if __name__ == '__main__':
    main()
