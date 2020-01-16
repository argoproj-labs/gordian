import logging
import sys
import argparse
from .transformations import SearchAndReplace
from .config import Config
from .repo import Repo
from github import GithubException

logger = logging.getLogger('gordian')
ch = logging.StreamHandler()
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('[%(asctime)-15s] %(levelname)s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class VerboseLogging(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         nargs=0,
                         const=True,
                         default=None,
                         required=False)

    def __call__(self, parser, namespace, values, option_string=None):
        logger.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)-15s] %(module)s.%(funcName)s %(levelname)s %(message)s')
        logger.handlers[0].setFormatter(formatter)


def get_basic_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-c', '--config',
        required=False,
        default='config.yaml',
        dest='config_file',
        help='Config file path.'
    )
    parser.add_argument(
        '-g', '--github-api',
        required=False,
        dest='github_api',
        help='Github API URL'
    )
    parser.add_argument(
        '--pr',
        required=True,
        dest='pr_message',
        help='Pull request name.'
    )
    parser.add_argument(
        '-v', '--verbose',
        required=False,
        action=VerboseLogging,
        dest='verbose',
        help='Enable debug output'
    )
    parser.add_argument(
        '-d', '--dry-run',
        required=False,
        action='store_true',
        dest='dry_run',
        help='Enable dry run mode'
    )
    parser.add_argument(
        '-b', '--branch',
        required=False,
        dest='branch',
        help='Branch name to use'
    )
    bumpers = parser.add_mutually_exclusive_group(required=False)
    bumpers.add_argument(
            '-M', '--major',
            dest='major',
            action='store_true',
            help='Bump the major version.'
        )
    bumpers.add_argument(
            '-m', '--minor',
            dest='minor',
            action='store_true',
            help='Bump the minor version.'
        )
    bumpers.add_argument(
            '-p', '--patch',
            dest='patch',
            action='store_true',
            help='Bump the patch version.'
        )
    return parser


def create_parser(args):
    parser = get_basic_parser()

    parser.add_argument(
        '-s', '--search',
        required=True,
        action='append',
        dest='search',
        help='The string to search for in config files.'
    )
    parser.add_argument(
        '-r', '--replace',
        required=True,
        action='append',
        dest='replace',
        help='The string that will replace instances of the searched string.'
    )

    args = parser.parse_args(args)
    if len(args.search) != len(args.replace):
        raise argparse.ArgumentTypeError('Number of search and replace arguments must be the same!')
    return args


def apply_transformations(args, transformations):
    config = Config(args.config_file)

    data = config.get_data()
    for repo_name in data:
        logger.info(f'Processing repo: {repo_name}')
        repo = Repo(repo_name, github_api_url=args.github_api, branch=args.branch)
        for transformation in transformations:
            transformation(args, repo).run()
        if repo.dirty:
            repo.bump_version(args.major, args.minor, args.patch, args.dry_run)
            if not args.dry_run:
                try:
                    repo.repo.create_pull(args.pr_message, '', 'master', repo.branch_name)
                    logger.info(f'PR created: {args.pr_message}. Branch: {repo.branch_name}')
                except GithubException as e:
                    logger.info(f'PR already exists for {repo.branch_name}')


def main():
    args = create_parser(sys.argv[1:])
    apply_transformations(args, [SearchAndReplace])


if __name__ == '__main__':
    main()
