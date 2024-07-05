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


def start(*rules):
    res = ''
    for r in rules:
        res += str(r) + '\n'
    return res


def propositions(p):
    return p


def there_is_clause(entity):
    return Fact(entity)


def constant(string, attribute_value):
    return Constant(string, attribute_value)


def constraint(constraint_body, whenever_clause):
    if not isinstance(constraint_body, list):
        constraint_body = [constraint_body]
    if not isinstance(whenever_clause, list):
        whenever_clause = [whenever_clause]
    return Constraint(constraint_body + whenever_clause) if whenever_clause else Constraint(constraint_body)


def whenever_then_clause_choice(whenever_clause, cardinality, then_subject, then_object):
    if not isinstance(whenever_clause, list):
        whenever_clause = [whenever_clause]
    if not isinstance(then_object, list):
        then_object = [then_object]
    whenever_then_clause_choice = Choice(then_subject, whenever_clause, then_object)
    if cardinality:
        whenever_then_clause_choice.lb = cardinality[0]
        whenever_then_clause_choice.ub = cardinality[1]
    return whenever_then_clause_choice


def whenever_then_clause_assignment(whenever_clause, then_subject):
    return Assignment([then_subject], whenever_clause)


def weak_constraint(level, comparison, whenever_clause):
    body = [comparison]
    if whenever_clause:
        if not isinstance(whenever_clause, list):
            whenever_clause = [whenever_clause]
        body += whenever_clause
    return WeakConstraint(body, level, [1])


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def comparison_operator(*args):
    items_dict = {'equal to': '==', 'different from': '!=', 'lower than': '<', 'greater than': '>',
                  'lower than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def entity(negation, name, attributes):
    entity = Atom(CnlWizardCompiler.signatures[name])
    for name, value in attributes:
        entity.fields[name] = value
    if negation:
        entity.negation = 'not '
    return entity


def cardinality(*value):
    value = ' '.join(value)
    if value == 'exactly one':
        return '1', '1'
    elif value == 'at least one':
        return '1', ''
    else:
        return '', '1'


def level(*value):
    value = ' '.join(value)
    if value == 'low':
        return '1'
    elif value == 'medium':
        return '2'
    else:
        return '3'


def aggregate_operator(*value):
    value = ' '.join(value)
    if value == 'the number of':
        return 'count'
    elif value == 'the total of':
        return 'sum'
    elif value == 'the lowest value of':
        return 'min'
    else:
        return 'max'


def verb(name, attributes, string):
    verb = Atom(CnlWizardCompiler.signatures[name + string])
    for parameter in attributes:
        verb.fields[parameter[0]] = parameter[1]
    return verb


def aggregate(aggregate_operator, attribute_name, entity):
    parameter_value = entity.fields[attribute_name]
    return Aggregate(aggregate_operator, [parameter_value], [entity])


def negation(args):
    return True



def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

def then_object_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

def whenever_clause_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

def disjunction_then_subject_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res

