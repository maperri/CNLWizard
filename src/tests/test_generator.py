import os
import unittest

from CNLWizard.cnl_wizard_generator import CnlWizardGenerator
from tests.utils import py_func_str


class TestCNLWizardGenerator(unittest.TestCase):

    def test(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, 'res', 'expected_lang1.py'), 'r') as file:
            expected_lang1 = file.read()
        with open(os.path.join(base_path, 'res', 'expected_lang2.py'), 'r') as file:
            lang2 = file.read()
        cnl_wizard = CnlWizardGenerator(os.path.join(base_path, 'res',
                                                     'cnlwizard_generator_test.yaml'),
                                        [os.path.join(base_path, 'import')],
                                        os.path.join(base_path, 'res'))
        self.maxDiff = None
        cnl_wizard.generate()
        # Add arithmetic function to lang1 file
        # It has no non-terminal symbols, but it is written in lower case.
        # Instead, TERMINAL rule, as it is upper case, it is not added
        with open(os.path.join(base_path, 'res', 'py_lang1.py'), 'r') as file:
            generated_py_lang1_content = file.read()
        with open(os.path.join(base_path, 'res', 'py_lang1.py'), 'w') as file:
            file.write('')  # restore file
        with open(os.path.join(base_path, 'res', 'py_lang2.py'), 'r') as file:
            generated_py_lang2_content = file.read()
        with open(os.path.join(base_path, 'res', 'py_lang2.py'), 'w') as file:
            file.write('')  # restore file

        self.assertEqual(generated_py_lang1_content, expected_lang1)
        self.assertEqual(generated_py_lang2_content, lang2)
        with open(os.path.join(base_path, 'res', 'grammar_lang1.lark'), 'r') as file:
            # as there is an instance of entity called entity, we do not have to add
            # a composite rule in lark
            grammar = file.read()
            self.assertTrue('entity: ("a" | "an")? string attribute | entity' not in grammar)
            self.assertTrue('there_is_clause: ("it is" | "There") "is" entity' in grammar)
            # dummy is unused, thus it is not added
            self.assertTrue('dummy' not in file.read())

