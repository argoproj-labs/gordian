<div align="center">
<img width="200"
src=".github/gordian-logo.png">
</div>

Gordian
========

[![Latest Release](https://img.shields.io/github/v/release/argoproj-labs/gordian.svg)](https://github.com/argoproj-labs/gordian/releases/)
[![Latest PyPi Version](https://badge.fury.io/py/gordian.svg)](https://pypi.python.org/pypi/gordian/)
[![codecov](https://codecov.io/gh/argoproj-labs/gordian/branch/master/graph/badge.svg)](https://codecov.io/gh/argoproj-labs/gordian/)
[![Build Status](https://github.com/argoproj-labs/gordian/workflows/Python%20package/badge.svg)](https://github.com/argoproj-labs/gordian/actions?query=workflow%3A%22Python+package%22)

Gordian applies transformations to files in github repositories and create PRs for the owners of the repositories review and merge them.

This project grew from a need to keep k8s onboarded services consistent and roll out changes at scale, so the main use case for this tool
is to be able to update the kustomize configuration for all our services.

This module installs two executables:
    - `gordian` can search and replace strings from files.
    - `pulpo` can apply more complex transformations based on the jsonpatch standard (https://tools.ietf.org/html/rfc6902#page-4)

It is designed with extensibility in mind, here is an example how to extend it to configure the HPA min/max values of our deployments to not scale.

```python
import sys
from gordian.gordian import get_basic_parser, apply_transformations
from gordian.transformations import Transformation

class PreScale(Transformation):

    def __init__(self, args, repo):
        super().__init__(args, repo)
        self.environments = args.environments

    def run(self):
        changes = False
        for f in self.repo.files:
            if not re.match(f'overlays/{self.environments}/envconfig-values.yaml', f.path):
                continue

            k8s_patches = list(yaml.safe_load_all(f.decoded_content))
            for r in k8s_patches:
                if r['kind'] != 'HorizontalPodAutoscaler':
                    continue

                if r['spec']['minReplicas'] != r['spec']['maxReplicas']:
                    r['spec']['maxReplicas'] = r['spec']['minReplicas']
                    message = f"Setting maxRelicas = minReplicas = {r['spec']['minReplicas']}"
                    changes = True

                break

            if changes:
                file_str = yaml.dump_all(k8s_patches, default_flow_style=False, explicit_start=True)
                self.repo.update_file(f, file_str, message, self.dry_run)


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


Installation
============
```
pip install gordian
```

Docker image
============
```
docker run --rm -it gordian:0.4.2 -h
usage: gordian [-h] [-c CONFIG_FILE] --pr PR_MESSAGE [-v] [-d] [-M | -m | -p]
                -s SEARCH -r REPLACE

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        Config file path. (default: config.yaml)
  --pr PR_MESSAGE       Pull request name. (default: None)
  -v, --verbose
  -d, --dry-run         Enable dry run mode (default: False)
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

Pulpo
=====
Example: Changing the values for the metrics in HPA object.
```
# pulpo -c all_servicies.yaml --pr 'Scaling at 80% CPU not 13%' json_patch.json
[2019-10-07 22:54:24,978] INFO Processing repo: rrodriquez/consumer-tax-documents-iks-config
[2019-10-07 22:54:26,777] INFO Path name: service/global-values.yaml
[2019-10-07 22:54:26,930] INFO Detected changes: {'values_changed': {"root['spec']['metrics'][0]['object']['target']['value']": {'new_value': 13, 'old_value': 80}, "root['spec']['metrics'][1]['object']['target']['value']": {'new_value': 13, 'old_value': 80}}}
[2019-10-07 22:54:26,942] INFO Applied json patch defined in json_patch.json
[2019-10-07 22:54:28,528] INFO Path name: service/kustomization.yaml
[2019-10-07 22:54:28,652] INFO Path name: overlays/cpf-usw2/envconfig-values.yaml
[2019-10-07 22:54:28,790] INFO Path name: overlays/cpf-usw2/kustomization.yaml
[2019-10-07 22:54:28,920] INFO Path name: overlays/cqa-usw2/envconfig-values.yaml
[2019-10-07 22:54:29,075] INFO Path name: overlays/cqa-usw2/kustomization.yaml
[2019-10-07 22:54:29,198] INFO Path name: overlays/dev-usw2/envconfig-values.yaml
[2019-10-07 22:54:29,319] INFO Path name: overlays/dev-usw2/kustomization.yaml
[2019-10-07 22:54:29,467] INFO Path name: overlays/pf-usw2/envconfig-values.yaml
[2019-10-07 22:54:29,601] INFO Path name: overlays/pf-usw2/kustomization.yaml
[2019-10-07 22:54:29,730] INFO Path name: overlays/prd-use2/envconfig-values.yaml
[2019-10-07 22:54:29,850] INFO Path name: overlays/prd-use2/kustomization.yaml
[2019-10-07 22:54:29,987] INFO Path name: overlays/prd-usw2/envconfig-values.yaml
[2019-10-07 22:54:30,171] INFO Path name: overlays/prd-usw2/kustomization.yaml
[2019-10-07 22:54:30,298] INFO Path name: overlays/qa-usw2/envconfig-values.yaml
[2019-10-07 22:54:30,423] INFO Path name: overlays/qa-usw2/kustomization.yaml
[2019-10-07 22:54:30,558] INFO Path name: service/files/mystiko-sigsci.yaml
[2019-10-07 22:54:30,699] INFO Path name: overlays/prd-use2/files/mystiko-service.yaml
[2019-10-07 22:54:30,821] INFO Path name: overlays/prd-usw2/files/mystiko-service.yaml
[2019-10-07 22:54:31,524] INFO PR created: Scaling at 80% CPU not 13%
#
```
The content of the `json_patch.json` in the previous execution is:
```json
[
  {"op": "test", "path": "/kind", "value": "HorizontalPodAutoscaler"},
  {"op": "replace", "path": "/spec/metrics/0/object/target/value", "value": 80},
  {"op": "replace", "path": "/spec/metrics/1/object/target/value", "value": 80}
]
```


```
docker run --rm -it --entrypoint pulpo gordian:0.4.2 -h
usage: pulpo [-h] [-c CONFIG_FILE] --pr PR_MESSAGE [-v] [-d] [-M | -m | -p]
             [-f FILE_REGEXP]
             patch_path

positional arguments:
  patch_path            Path to the json patch file.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        Config file path. (default: config.yaml)
  --pr PR_MESSAGE       Pull request name. (default: None)
  -v, --verbose
  -d, --dry-run         Enable dry run mode (default: False)
  -M, --major           Bump the major version. (default: False)
  -m, --minor           Bump the minor version. (default: False)
  -p, --patch           Bump the patch version. (default: False)
  -f FILE_REGEXP, --filter FILE_REGEXP
                        This regular expression will be used to filter the
                        files to apply the transformation. (default: .*\.yaml)
```

Development
===========
The simplest way to hit the ground running if you want to contribute with code is using docker, launch a python container:
```
localhost$ docker run --rm -it  -v $(pwd):$(pwd) -w $(pwd) python:3.7-stretch bash
```

Install the project and test dependencies in developer mode:
```
container# pip install -e .[test]
```

Run the tests:
```
container# pytest
=========================================== test session starts ============================================
platform linux -- Python 3.7.1, pytest-4.5.0, py-1.8.0, pluggy-0.11.0
rootdir: /Users/rrodriquez/git/argoproj-labs
plugins: requests-mock-1.6.0, cov-2.7.1
collected 33 items

....
================================== 33 passed, 2 warnings in 1.73 seconds ===================================
```

Happy hacking!!
