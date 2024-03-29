from . import BaseFile
import yaml


class YamlFile(BaseFile):
    def __init__(self, github_file, repo):
        super().__init__(github_file, repo)
        yaml.add_representer(type(None), represent_none)

    def _load_objects(self):
        return list(yaml.safe_load_all(self.file_contents))

    def _dump(self, serialize_options={}):
        default_flow_style = serialize_options.get("default_flow_style", False)
        explicit_start = serialize_options.get("explicit_start", True)
        return yaml.dump_all(
            self.objects,
            default_flow_style=default_flow_style,
            explicit_start=explicit_start,
        )


def represent_none(self, _):
    # Disable dumping 'null' string for null values
    # Taken from here: https://stackoverflow.com/a/41786451
    return self.represent_scalar("tag:yaml.org,2002:null", "")
