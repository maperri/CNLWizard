import os.path
import unittest

from CNLWizard.reader import YAMLReader, pyReader


class TestReader(unittest.TestCase):

    def test_yaml_reader(self):
        cnl = YAMLReader().read_specification(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                           'res', 'yaml_reader_test.yaml'))
        lang1 = [(x.name, x.syntax) for x in cnl._grammar.get_rules('lang1')]
        self.assertIn(('negative_constraint', ['"It is prohibited that" operation']), lang1)
        self.assertIn(('constraint', ['negative_constraint']), lang1)
        self.assertIn(('arithmetic', ['"the sum between 1 and 2"', '"the difference between 1 and 2"']), lang1)
        self.assertIn(('operation', ['arithmetic', 'boolean']), lang1)
        self.assertIn(('boolean', ['"the or between a and b"']), lang1)
        self.assertIn(('start', ['arithmetic', 'constraint']), lang1)

        lang2 = [(x.name, x.syntax) for x in cnl._grammar.get_rules('lang2')]
        self.assertIn(('negative_constraint', ['"It is prohibited that" operation']), lang2)
        self.assertIn(('constraint', ['negative_constraint']), lang2)
        self.assertIn(('arithmetic', ['"the sum between 1 and 2"', '"the difference between 1 and 2"']), lang2)
        self.assertIn(('operation', ['arithmetic']), lang2)
        self.assertIn(('start', ['arithmetic', 'constraint']), lang2)

    def test_py_reader(self):
        reader = pyReader()
        self.assertEqual({'arith', 'Operation', 'constraint', 'Proposition'},
                         set(reader.read_module(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'res', 'functions.py'))))