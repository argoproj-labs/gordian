import base64
from github import ContentFile

class Utils:

    @staticmethod
    def create_github_content_file(file=None):
        file = file or 'content.yaml'
        f = open(f'./tests/fixtures/{file}', 'r')
        contents = str(base64.b64encode(bytearray(f.read(), 'utf-8')), 'utf-8')
        attributes = {'name': file, 'path': f'/{file}','encoding': 'base64','content': contents}
        return ContentFile.ContentFile(None, {}, attributes, completed=True)
