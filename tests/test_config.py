import unittest
from gordian.config import Config

class TestConfig(unittest.TestCase):

    def test_get_data(self):
        test_return = ['testOrg/TestService1', 'testOrg/TestService2']
        config = Config('./tests/fixtures/test_config.yaml')
        data = config.get_data()
        self.assertEqual(data, test_return)
