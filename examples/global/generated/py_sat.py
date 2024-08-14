from pysat.formula import CNF, Atom, Neg
from sympy.logic.boolalg import to_cnf

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


class Definition:
    def __init__(self, entity):
        self.name = entity.name
        self.fields = entity.fields
        self.negation = ''

    def __str__(self):
        return f'{self.negation}{self.name}_{"_".join(self.fields.values())}'


class Clause:
    def __init__(self, clause):
        self.clause = clause

    def __str__(self):
        return f'({self.clause})'


def constraint(clausebody):
    return Clause(clausebody)


def sat_formula(r):
    return Clause(r)


def there_is_clause(entity):
    return Clause(entity)


def if_then(clausebody, clausebody_2):
    return Clause(f'{clausebody}>>{clausebody_2}')


def propositions(args):
    return args


def start(*formula_body):
    formula_body = "&".join(["(" + str(x) + ")" for x in formula_body])
    formula_body = str(to_cnf(formula_body))
    definitions = []
    formula = CNF()
    for clause in formula_body.split("&"):
        literals = []
        for atom in clause.split("|"):
            atom_name = atom.strip().removeprefix("(").removesuffix(")")
            is_negated = atom_name.startswith("~")
            atom_name = atom_name.removeprefix("~")
            literal = Atom(atom_name)
            if is_negated:
                literal = Neg(literal)
                literal.clausify()
                literals.append(literal.clauses[0][0])
            else:
                literal.clausify()
                literals.append(literal.name)
            if atom_name not in definitions:
                literal_name = literal.name if not is_negated else abs(literal.clauses[0][0])
                formula.comments.append("c " + str(literal_name) + " " + atom_name)
                definitions.append(atom_name)
        formula.append(literals)
    return formula.to_dimacs()


def simple_clause(entity, negation, entity_2):
    for key, value in entity.fields.items():
        field_name = entity.name + key
        entity_2.fields[field_name] = value
    return Clause("~" + str(entity_2)) if negation else Clause(str(entity_2))


def formula_operator(*args):
    items_dict = {'and': '&', 'or': '|', 'imply': '>>', 'implies': '>>', 'is equivalent to': '<->', 'not': '~'}
    item = ' '.join(args)
    return items_dict[item]


def formula(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Clause(operator.join(map(str, args)))


def entity(name, attributes):
    try:
        entity = CnlWizardCompiler.signatures[name]
        for name, value in attributes:
            entity.fields[name] = value
        return Definition(entity)
    except KeyError:
        return None


def negation(*args):
    return True


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

def clause_body(there_is_clause):
   return there_is_clause

