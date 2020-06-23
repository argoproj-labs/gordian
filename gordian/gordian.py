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
    parser.add_argument(
        '-t', '--target-branch',
        required=False,
        default='master',
        dest='target_branch',
        help='Target branch'
    )
    parser.add_argument(
        '-l','--labels',
        required=False,
        default=[],
        nargs='+',
        dest='pr_labels',
        help='List of space separated label names you wish to add to your pull request(s)'
    )
    bumpers = parser.add_mutually_exclusive_group(required=False)
    bumpers.add_argument(
            '-M', '--major',
            dest='semver_label',
            action='store_const',
            const='major',
            help='Bump the major version.'
        )
    bumpers.add_argument(
            '-m', '--minor',
            dest='semver_label',
            action='store_const',
            const='minor',
            help='Bump the minor version.'
        )
    bumpers.add_argument(
            '-p', '--patch',
            dest='semver_label',
            action='store_const',
            const='patch',
            help='Bump the patch version.'
        )
    pr_desc = parser.add_mutually_exclusive_group(required=False)
    pr_desc.add_argument(
            '--description',
            default='',
            dest='description',
            help='Description to be passed to the PR.'
        )
    pr_desc.add_argument(
            '--description-file',
            dest='description_file',
            help='Local file path for the description to be passed to the PR.'
        )
    parser.add_argument(
        '--force-changelog',
        required=False,
        dest='force_changelog',
        help='Fail if changelog does not exist or cannot be parsed'
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

def apply_transformations(args, transformations, pr_created_callback=None):
    config = Config(args.config_file)
    pr_description = get_pr_description(args)
    transform(args, transformations, config.get_data(), pr_description, pr_created_callback=pr_created_callback)

def get_pr_description(args):
    if args.description_file is not None:
        with open(args.description_file,'r') as fh:
            return fh.read()
    return args.description

def transform(args, transformations, repositories, pr_description, pr_created_callback):
    pull_request_urls = []
    for repo_name in repositories:
        logger.info(f'Processing repo: {repo_name}')
        repo = Repo(repo_name, github_api_url=args.github_api, branch=args.branch, semver_label=args.semver_label, target_branch=args.target_branch)
        for transformation in transformations:
            transformation(args, repo).run()
        if repo.dirty:
            repo.bump_version(args.dry_run)
            if not args.dry_run:
                try:
                    pull_request = repo.create_pr(args.pr_message, pr_description, args.target_branch, args.pr_labels)
                    pull_request_urls.append(pull_request.html_url)
                    if pr_created_callback is not None:
                        logger.debug(f'Calling post pr created callback with: {pull_request}, {repo.branch_name}')
                        pr_created_callback(repo_name, pull_request)
                    logger.info(f'PR created: {args.pr_message}. Branch: {repo.branch_name}. Labels: {args.pr_labels}')
                except GithubException as e:
                    logger.info(f'PR already exists for {repo.branch_name}. Error: {e}')

    if pull_request_urls:
        logger.info('Pull requests')
        [ logger.info(url) for url in pull_request_urls ]


def main():
    args = create_parser(sys.argv[1:])
    apply_transformations(args, [SearchAndReplace])

if __name__ == '__main__':
    main()
