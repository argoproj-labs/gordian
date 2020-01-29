<div align="center">
<img width="200"
src=".github/gordian-logo.png">
</div>

Gordian
========

[![Latest Release](https://img.shields.io/github/v/release/argoproj-labs/gordian.svg)](https://github.com/argoproj-labs/gordian/releases/)
[![Latest PyPi Version](https://badge.fury.io/py/gordian.svg)](https://pypi.python.org/pypi/gordian/)
[![codecov](https://codecov.io/gh/argoproj-labs/gordian/branch/master/graph/badge.svg)](https://codecov.io/gh/argoproj-labs/gordian/)
[![Python Build Status](https://github.com/argoproj-labs/gordian/workflows/Python%20package/badge.svg)](https://github.com/argoproj-labs/gordian/actions?query=workflow%3A%22Python+package%22)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/argoprojlabs/gordian.svg)](https://hub.docker.com/repository/docker/argoprojlabs/gordian)

Gordian applies transformations to files in github repositories and create PRs for the owners of the repositories to review and merge them.

This project grew from a need to keep various kubernetes services consistent and roll out changes at scale. The main use case for this tool is to make changes to configuration files across multiple repositories simultaneously.

# Use Cases

## Search and Replace

You can use the docker image to search and replace various strings across repositories.

```
docker run --rm -it argoprojlabs/gordian:latest -h
usage: gordian [-h] [-c CONFIG_FILE] [-g GITHUB_API] --pr PR_MESSAGE [-v] [-d]
               [-b BRANCH] [-M | -m | -p] -s SEARCH -r REPLACE

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        Config file path. (default: config.yaml)
  -g GITHUB_API, --github-api GITHUB_API
                        Github API URL (default: None)
  --pr PR_MESSAGE       Pull request name. (default: None)
  -v, --verbose
  -d, --dry-run         Enable dry run mode (default: False)
  -b BRANCH, --branch BRANCH
                        Branch name to use (default: None)
  -M, --major           Bump the major version. (default: False)
  -m, --minor           Bump the minor version. (default: False)
  -p, --patch           Bump the patch version. (default: False)
  -s SEARCH, --search SEARCH
                        The string to search for in config files. (default:
                        None)
  -r REPLACE, --replace REPLACE
                        The string that will replace instances of the searched
                        string. (default: None)
```

## Complex transformations

You can use the interface to script complex changes across various JSON and YAML files, as shown in this example that modifies a kubernetes resource. You can see more examples in the `examples` directory.

```python
import sys
from gordian.gordian import get_basic_parser, apply_transformations
from gordian.transformations import Transformation

class PreScale(Transformation):

    def __init__(self, args, repo):
        super().__init__(args, repo)
        self.environments = args.environments

    def run(self):
        for env in self.environments:
            file = self.repo.get_objects(f'overlays/{self.environments}/envconfig-values.yaml')

            for obj in file:
                if obj['kind'] != 'HorizontalPodAutoscaler':
                    continue

                if obj['spec']['minReplicas'] != obj['spec']['maxReplicas']:
                    obj['spec']['maxReplicas'] = obj['spec']['minReplicas']

            file.save(f'Setting maxRelicas = minReplicas = {obj['spec']['minReplicas']}', self.dry_run)


if __name__ == '__main__':
    parser = get_basic_parser()
    parser.add_argument(
        '-e', '--environments',
        required=False,
        dest='environments',
        default='prd-.*',
        help='Environments to update.'
    )
    args = parser.parse_args(sys.argv[1:])
    apply_transformations(args, [PreScale])
```

# Dependencies
- `config.yaml` (required) - list of repositories you wish to modify
- `GIT_USERNAME` (required) - your Github username
- `GIT_PASSWORD` (required) - Github personal access token that grants write access to the specified repositories

# Development
The simplest way to hit the ground running if you want to contribute with code is using docker, launch a python container
```
localhost$ docker run --rm -it  -v $(pwd):$(pwd) -w $(pwd) python:3.7-stretch bash
```

Install the project and test dependencies in developer mode
```
container# pip install -e .[test]
```

Run the tests
```
container# pytest
=========================================== test session starts ============================================
platform linux -- Python 3.7.1, pytest-4.5.0, py-1.8.0, pluggy-0.11.0
rootdir: /Users/user/git/argoproj-labs
plugins: requests-mock-1.6.0, cov-2.7.1
collected 33 items

....
================================== 33 passed, 2 warnings in 1.73 seconds ===================================
```

# Support

## Contributors
- [Rene Martin](https://github.com/agarfu)
- [Jonathan Nevelson](https://github.com/jnevelson)
- [Corey Caverly](https://github.com/coreycaverly)
- [Sara Blumin](https://github.com/sblumin)
