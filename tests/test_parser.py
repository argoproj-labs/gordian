import unittest
from gordian.gordian import create_parser

class TestParser(unittest.TestCase):

    def test_no_args(self):
        with self.assertRaises(SystemExit):
            create_parser([])

    def test_just_config(self):
        with self.assertRaises(SystemExit):
            create_parser(['-c', './gordian/config/ex_config.yaml', '--pr', ''])

    def test_just_search(self):
        with self.assertRaises(SystemExit):
            create_parser(['-s', 'test'])

    def test_just_gordian(self):
        with self.assertRaises(SystemExit):
            create_parser(['-r', 'test'])

    def test_config_and_search(self):
        with self.assertRaises(SystemExit):
            create_parser(['-c', './gordian/config/ex_config.yaml', '-s', 'test'])

    def test_config_and_repace(self):
        with self.assertRaises(SystemExit):
            create_parser(['-c', './gordian/config/ex_config.yaml', '-r', 'test'])

    def test_search_and_gordian(self):
        args = create_parser(['-s', 'hello', '-r', 'goodbye', '--pr', 'test'])
        self.assertEqual(args.config_file, 'config.yaml')
        self.assertEqual(args.search, ['hello'])
        self.assertEqual(args.replace, ['goodbye'])

    def test_all_args(self):
        args = create_parser(['-c', './gordian/config/ex_config.yaml', '-s', 'hello', '-r', 'goodbye', '--pr', 'test'])
        self.assertEqual(args.config_file, './gordian/config/ex_config.yaml')
        self.assertEqual(args.search, ['hello'])
        self.assertEqual(args.replace, ['goodbye'])
