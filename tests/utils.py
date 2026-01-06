import base64
from github import ContentFile
from unittest.mock import MagicMock

class Utils:

    @staticmethod
    def create_github_content_file(file=None):
        file = file or 'content.yaml'
        f = open(f'./tests/fixtures/{file}', 'r')
        contents = str(base64.b64encode(bytearray(f.read(), 'utf-8')), 'utf-8')
        attributes = {'name': file, 'path': f'/{file}','encoding': 'base64','content': contents}
        requester = MagicMock()
        requester.is_not_lazy = True
        return ContentFile.ContentFile(requester, {}, attributes, completed=True)
