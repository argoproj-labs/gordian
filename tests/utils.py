import base64
from github import ContentFile

class Utils:

    def create_github_content_file():
        f = open('./tests/fixtures/content.yaml', 'r')
        contents = str(base64.b64encode(bytearray(f.read(), 'utf-8')), 'utf-8')
        attributes = {'name':'content.yaml', 'path':'/content.yaml','encoding':'base64','content': contents}
        return ContentFile.ContentFile(None, {}, attributes, completed=True)
