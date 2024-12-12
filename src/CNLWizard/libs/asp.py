from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


class Atom:
    def __init__(self, entity):
        self.name: str = entity.name
        self.fields: dict = entity.fields
        self.negation: str = ''

    def __str__(self):
        return f'{self.negation}{self.name}({",".join(self.fields.values())})'


class Fact:
    def __init__(self, head):
        self.head: Atom = head

    def __str__(self):
        return f'{self.head}.'


class Constant:
    def __init__(self, name, value):
        self.name: str = name
        self.value: str = value

    def __str__(self):
        return f'#const {self.name}={self.value}.'


class Constraint:
    def __init__(self, atoms):
        self.atoms = atoms

    def __str__(self):
        return f':- {", ".join(map(str, self.atoms))}.'


class Aggregate:
    def __init__(self, operator, discriminant, body):
        self.operator: str = operator
        self.discriminant: list = discriminant
        self.body: list = body

    def __str__(self):
        return f'#{self.operator}{{{", ".join(map(str, self.discriminant))}: {", ".join(map(str, self.body))}}}'


class Choice:

    def __init__(self, head, body, condition, lb='', ub=''):
        self.head: Atom = head
        self.body: list = body
        self.condition: list = condition
        self.lb: str = lb
        self.ub: str = ub

    def __str__(self):
        head_cond = ": " + ", ".join(map(str, self.condition)) if self.condition else ''
        return f'{self.lb} {{{self.head}{head_cond}}} {self.ub} :- {", ".join(map(str, self.body))}.'


class Assignment:

    def __init__(self, head, body):
        self.head: list = head
        self.body: list = body

    def __str__(self):
        return f'{" | ".join(map(str, self.head))} :- {", ".join(map(str, self.body))}.'


class WeakConstraint:
    def __init__(self, body, weight, discriminant):
        self.body: list = body
        self.weight: int = weight
        self.discriminant: list = discriminant

    def __str__(self):
        return f':~ {", ".join(map(str, self.body))}. [{self.weight}@{", ".join(map(str, self.discriminant))}]'


def entity(string, attribute):
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def there_is_clause(entity):
    return Fact(entity)


def verb(string_1, attribute, string_2):
    entity = Atom(CnlWizardCompiler.signatures[string_1.lower()])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    return Aggregate('sum', [args[1][0]], args[1][1:])


def comparison_operator(*args):
    items_dict = {'equal to': '!=',
                  'different from': '==',
                  'less than': '>=',
                  'greater than': '<=',
                  'less than or equal to': '>',
                  'greater than or equal to': '<'}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Constraint([operator.join(map(str, args))])


def simple_proposition(entity_1, entity_2, entity_3):
    return entity_1, entity_2, entity_3


def negated_simple_proposition(entity_1, entity_2, entity_3):
    entity_2.negation = 'not '
    return entity_1, entity_2, entity_3
