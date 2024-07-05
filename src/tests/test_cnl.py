import os
import unittest

from CNLWizard.cnl import CompiledRule
from CNLWizard.reader import pyReader


class TestCnl(unittest.TestCase):

    def test_CompiledRule(self):
        rule = CompiledRule('test', ['"terminal" non_terminal'])
        self.assertEqual(['non_terminal'], rule.get_non_terminal_symbols())
        rule = CompiledRule('test', ['non_terminal'])
        self.assertEqual(['non_terminal'], rule.get_non_terminal_symbols())
        rule = CompiledRule('test', ['TERMINAL non_terminal "terminal" non_terminal TERMINAL '
                                     '"terminal" "terminal" non_terminal'])
        self.assertEqual(['non_terminal', 'non_terminal', 'non_terminal'], rule.get_non_terminal_symbols())

    def test_py_reader(self):
        reader = pyReader()
        self.assertEqual({'arith', 'Operation', 'constraint', 'Proposition'},
                         set(reader.read_module(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'res', 'functions.py'))))
