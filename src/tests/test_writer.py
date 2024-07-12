import unittest

from CNLWizard.cnl import CompiledRule
from CNLWizard.writer import PythonFunctionWriter
from tests.utils import py_func_str


class TestYAMLWriter(unittest.TestCase):


    def test_py_writer_func(self):
        py_writer = PythonFunctionWriter()
        self.assertEqual(py_writer.visit_compiled_rule(CompiledRule('test', ['attr attr'])), py_func_str('test', ['attr', 'attr_2']))
        self.assertEqual(py_writer.visit_compiled_rule(CompiledRule('test', ['attr ATTR attr'])), py_func_str('test', ['attr', 'attr_2']))
        self.assertEqual(py_writer.visit_compiled_rule(CompiledRule('test', ['attr "attr" attr'])), py_func_str('test', ['attr', 'attr_2']))
