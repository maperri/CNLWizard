import unittest
from textwrap import dedent

from lark.exceptions import VisitError

from CNLWizard.ProcessCNL import process_cnl_specification
from CNLWizard.CNLWizard import Signatures, cnl_type, Cnl


class CnlTest(unittest.TestCase):

    def test_signatures(self):
        signatures = Signatures()
        signatures['atom'] = 'atom', ['id', 'value'], ['id'], ''
        self.assertEqual(str(signatures['atom']), 'atom(_,_)')
        atom = signatures['atom']
        atom.fields['id'] = '1'
        self.assertEqual(str(atom), 'atom(1,_)')
        self.assertEqual(str(signatures['atom']), 'atom(_,_)')

        class Atom:
            def __init__(self, name: str, fields: dict):
                self.name = name
                self.fields = fields

            def __str__(self):
                return f'{self.name}[{",".join(self.fields.values())}]'

        signatures = Signatures(Atom)
        signatures['atom'] = 'atom', ['id', 'value'], ['id'], ''
        self.assertEqual(str(signatures['atom']), 'atom[_,_]')

        signatures = Signatures(signature_field_null_value='*')
        signatures['atom'] = 'atom', ['id', 'value'], ['id'], ''
        self.assertEqual(str(signatures['atom']), 'atom(*,*)')


    def test_cnl_type_definition(self):
        @cnl_type('{self.name}({",".join(self.fields.values())}).')
        class Atom:
            name: str
            fields: dict

        atom = Atom('atom', {'id': '1'})
        self.assertEqual(str(atom), 'atom(1).')

    def test_grammar(self):
        cnl = Cnl()
        cnl.support_rule('start', 'entity')
        @cnl.rule('["a "|"an "] CNAME')
        def entity(name):
            return name
        cnl.support_rule('rule', 'body1', 'body2', concat=',')
        self.assertEqual(str(cnl._grammar), dedent('''\
                                                    %import common.WS
                                                    %ignore WS
                                                    %import common.CNAME
                                                    signature_parameters: ("a" | "an")? CNAME
                                                                        | signature_parameters "," signature_parameters -> signature_parameters_concatenation
                                                    signature_definition: ("A" | "An")? CNAME ["is" ("a"|"an")? CNAME "concept, and it"] "is identified by" signature_parameters ["and has" signature_parameters] "."
                                                    ?cnl_start: signature_definition+ start
                                                    ?start: entity
                                                    entity: ["a "|"an "] CNAME
                                                    rule: body1
                                                        | body2
                                                        | rule "," rule -> rule_concatenation'''))

    def test_default_signature(self):
        cnl = Cnl()
        cnl.support_rule('start', 'entity+')
        @cnl.rule('("A"|"An") CNAME " with " CNAME " " CNAME "."')
        def entity(name, parameter_name, field1):
            atom = cnl.signatures[name]
            atom.fields[parameter_name] = field1
            return atom
        res = cnl.compile('An entity is identified by a name and has a value. '
                          'An entity with name X. An entity with name Y.')
        self.assertEqual(res.strip(), 'entity(X,_)\nentity(Y,_)')
        self.assertEqual(cnl.signatures["entity"].keys, ['name'])

    def test_process_cnl(self):
        '''
        Propositions ending with "where ..." are processed. The variable is substituted in the CNL specification.
        '''
        text = 'Some text. A node X, where X is one of blue, red and yellow.'
        self.assertEqual(process_cnl_specification(text), 'Some text.\nA node blue.\nA node red.\nA node yellow.\n')
        text = 'Some text. A node X, where X is between 1 and 3.'
        self.assertEqual(process_cnl_specification(text), 'Some text.\nA node 1 .\nA node 2 .\nA node 3 .\n')
        text = 'Some text. A node X and a node Y, where X is between 1 and 2, where Y is one of blue, red.'
        self.assertEqual(process_cnl_specification(text), 'Some text.\nA node 1 and a node blue.\nA node 1 and a node red.\nA node 2 and a node blue.\nA node 2 and a node red.\n')
        text = 'Some text. A node X and a node Y, where X is between 1 and 2, where Y is respectively one of blue, red.'
        self.assertEqual(process_cnl_specification(text),
                         'Some text.\nA node 1 and a node blue.\nA node 2 and a node red.\n')
        # Not matching lists
        with self.assertRaises(VisitError) as context:
            text = 'Some text. A node X and a node Y, where X is between 1 and 3, where Y is respectively one of blue, red.\n'
            process_cnl_specification(text)
            self.assertTrue('Lists do not match for variable substitution in proposition 2' in str(context.exception))




