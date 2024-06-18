import unittest
from textwrap import dedent

from lark.exceptions import VisitError

from CNLWizard.ProcessCNL import process_cnl_specification
from CNLWizard.CNLWizard import Signatures, cnl_type, Cnl


class CnlTest(unittest.TestCase):

    def setUp(self) -> None:
        Cnl.signatures = Signatures()

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

        @cnl_type()
        class Atom2:
            name: str
            fields: dict

            def __str__(self):
                return f'{self.name}({",".join(self.fields.values())}).'

        atom = Atom('atom', {'id': '1'})
        self.assertEqual(str(atom), 'atom(1).')
        atom2 = Atom2('atom', {'id': '1'})
        self.assertEqual(str(atom2), 'atom(1).')

    def test_grammar(self):
        cnl = Cnl()
        cnl.support_rule('start', 'entity')

        @cnl.rule('["a "|"an "] CNAME')
        def entity(name):
            return name

        cnl.support_rule('rule', 'body1', 'body2', concat=',')
        grammar = str(cnl._grammar)
        self.assertTrue('entity: ["a "|"an "] CNAME' in grammar and
                        dedent('''\
                                rule: body1
                                    | body2
                                    | rule "," rule -> rule_concatenation''') in grammar)

    def test_default_signature(self):
        cnl = Cnl()
        cnl.support_rule('start', 'entity+')

        @cnl.rule('("A"|"An") CNAME " with " CNAME " " CNAME "."')
        def entity(name, parameter_name, field1):
            atom = cnl.signatures[name]
            atom.fields[parameter_name] = field1
            return atom

        res = cnl.compile('An entity is identified by a name and has a value. '
                          'An intEntity1 is an integer concept, and it is identified by an id.'
                          'An intRangedEntity is an integer concept that ranges from 1 to 10, and it is identified by an id.'
                          'An entity with name X. An entity with name Y.')
        self.assertEqual(res.strip(), 'entity(X,_)\nentity(Y,_)')
        self.assertEqual(cnl.signatures["entity"].keys, ['name'])
        self.assertEqual(cnl.signatures["intEntity1"].type, 'integer')
        self.assertEqual(cnl.signatures["intRangedEntity"].lb, 1)
        self.assertEqual(cnl.signatures["intRangedEntity"].ub, 10)

    def test_process_cnl(self):
        """
        Propositions ending with "where ..." are processed. The variable is substituted in the CNL specification.
        """
        cnl = Cnl()
        text = 'Some text. A node X, where X is one of blue, red and yellow.'
        self.assertEqual(process_cnl_specification(cnl, text), 'Some text.\nA node blue.\nA node red.\nA node yellow.\n')
        text = 'Some text. A node X, where X is between 1 and 3.'
        self.assertEqual(process_cnl_specification(cnl, text), 'Some text.\nA node 1 .\nA node 2 .\nA node 3 .\n')
        text = 'Some text. A node X and a node Y, where X is between 1 and 2, where Y is one of blue, red.'
        self.assertEqual(process_cnl_specification(cnl, text),
                         'Some text.\nA node 1 and a node blue.\nA node 1 and a node red.\nA node 2 and a node blue.\nA node 2 and a node red.\n')
        text = 'Some text. A node X and a node Y, where X is between 1 and 2, where Y is respectively one of blue, red.'
        self.assertEqual(process_cnl_specification(cnl, text),
                         'Some text.\nA node 1 and a node blue.\nA node 2 and a node red.\n')
        # Not matching lists
        with self.assertRaises(VisitError) as context:
            text = 'Some text. A node X and a node Y, where X is between 1 and 3, where Y is respectively one of blue, red.\n'
            process_cnl_specification(cnl, text)
            self.assertTrue('Lists do not match for variable substitution in proposition 2' in str(context.exception))

    def test_default_components(self):
        cnl = Cnl()
        cnl.support_rule('start', '(entity | math_operation | comparison | formula) "."')
        cnl.support_rule('math_operand', 'NUMBER')
        cnl.support_rule('comparison_first', 'math_operation')
        cnl.support_rule('comparison_second', 'math_operation | NUMBER')
        cnl.support_rule('formula_first', 'entity')
        cnl.support_rule('formula_second', 'entity')

        res = cnl.compile('An entity is identified by an id.\n'
                          'an entity with id equal to 1 .')
        self.assertEqual(str(res), 'entity(1)')
        self.assertEqual(cnl.compile('the sum between 1 and 1 .'), '1+1')
        self.assertEqual(cnl.compile('the sum between 1 and 1 is equal to 1 .'), '1+1==1')
        self.assertEqual(cnl.compile('the sum between 1 and 1 is different from the difference between 1 and 1 .'), '1+1!=1-1')
        self.assertEqual(cnl.compile('entity with id equal to 1 and entity with id equal to 2'), 'entity(1)&entity(2)')

    def test_cnl_types(self):
        cnl = Cnl()
        # List
        cnl.support_rule('start', '(entity ".")*')
        res = cnl.compile('An entity is identified by an id.'
                    'A test is a list made of 1, 2 .\n'
                    'an entity with id equal to X, where X is one of test .')
        self.assertEqual(cnl.lists['test'][0], 1)
        self.assertEqual(cnl.lists['test'][1], 2)
        self.assertEqual(res, 'entity(1)\nentity(2)')


    def test_extend_default_components(self):
        @cnl_type('{self.negation}{self.name}({",".join(self.fields.values())})')
        class Atom:
            name: str
            fields: dict
            negation: str

        cnl = Cnl(signatures=Signatures(signature_type=Atom))

        @cnl.extends('[NEGATION] entity')
        def entity(negation, entity):
            if negation:
                entity.negation = 'not '
            return entity

        cnl.support_rule('start', '"There is" entity "."')
        cnl.support_rule("NEGATION", '"not"')
        res = cnl.compile('An entity is identified by an id.\n'
                          'There is not an entity with id equal to 1 .')
        self.assertEqual(str(res), 'not entity(1)')

    def test_terminal_symbols_dict(self):
        cnl = Cnl()
        cnl.support_rule('start', 'test "." ')
        cnl.support_rule('test', {
            '1': 1,
            '2': 2,
            '3': 3
        })
        self.assertEqual(cnl.compile('1 .'), '1')
        self.assertEqual(cnl.compile('2 .'), '2')
        self.assertEqual(cnl.compile('3 .'), '3')

    def test_modify_components(self):
        cnl = Cnl()
        cnl.support_rule('start', 'math_operation "."')
        cnl.support_rule('math_operand', 'NUMBER')
        cnl.math_operation['sum'] = ' PLUS '  # modifying existing operator
        cnl.math_operation['mod'] = ' % '  # adding new operator
        self.assertEqual(cnl.compile('the sum between 1 and 1 .'), '1 PLUS 1')
        self.assertEqual(cnl.compile('the mod between 1 and 1 .'), '1 % 1')
        def callable_operator(first, second):
            return f'OP({first},{second})'
        cnl.math_operation['OP'] = callable_operator
        self.assertEqual(cnl.compile('the OP between 1 and 2 .'), 'OP(1,2)')

