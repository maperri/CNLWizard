
import unittest

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, Signatures
from CNLWizard.process_cnl import process_cnl_specification


class TestPreprocess(unittest.TestCase):

    def test(self):
        cnl = CnlWizardCompiler()
        cnl.config = {'signatures': True, 'var_substitution': True}
        res = process_cnl_specification(cnl, 'A node is identified by an id.', cnl.config)
        self.assertEqual(str(cnl.signatures['node']), 'node(_)')
        self.assertEqual(res, '')
        CnlWizardCompiler.signatures = Signatures()
        cnl.config['signatures'] = False
        res = process_cnl_specification(cnl, 'A node is identified by an id.', cnl.config)
        self.assertEqual(res, 'A node is identified by an id.')
