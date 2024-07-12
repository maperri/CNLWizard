import os
import unittest

from CNLWizard.cnl_wizard_generator import CnlWizardGenerator
from CNLWizard.writer import PythonFunctionWriter
from tests.utils import py_func_str


class TestCNLWizardGenerator(unittest.TestCase):

    def test(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, 'res', 'py_lang1.py'), 'r') as file:
            lang1 = file.read()
        with open(os.path.join(base_path, 'res', 'py_lang2.py'), 'r') as file:
            lang2 = file.read()
        cnl_wizard = CnlWizardGenerator(os.path.join(base_path, 'res',
                                                     'cnlwizard_generator_test.yaml'),
                                        os.path.join(base_path, 'res'))

        cnl_wizard.generate()
        # Add arithmetic function to lang1 file
        # It has no non-terminal symbols, but it is written in lower case.
        # Instead, TERMINAL rule, as it is upper case, it is not added
        with open(os.path.join(base_path, 'res', 'py_lang1.py'), 'r') as file:
            self.assertEqual(file.read(), lang1 + py_func_str('arithmetic', ['*args']))
        with open(os.path.join(base_path, 'res', 'grammar_lang1.lark'), 'r') as file:
            # as there is an instance of entity called entity, we do not have to add
            # a composite rule in lark
            self.assertTrue('entity: ("a" | "an")? string attribute | entity' not in file.read())
            # dummy is unused, thus it is not added
            self.assertTrue('dummy' not in file.read())
        # Do not add anything to lang2 file
        with open(os.path.join(base_path, 'res', 'py_lang2.py'), 'r') as file:
            self.assertEqual(file.read(), lang2)
        # Restore files
        with open(os.path.join(base_path, 'res', 'py_lang1.py'), 'w') as file:
            file.write(lang1)
        with open(os.path.join(base_path, 'res', 'py_lang2.py'), 'w') as file:
            file.write(lang2)
