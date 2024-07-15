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


def there_is_clause(entity):
   return Fact(entity)


def constant(string, attribute_value):
   return Constant(string, attribute_value)


def constraint(constraint_body, whenever_clause):
    if constraint_body and not isinstance(constraint_body, list):
        constraint_body = [constraint_body]
    if whenever_clause and not isinstance(whenever_clause, list):
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


def propositions(there_is_clause):
   return there_is_clause


def attribute_value(string):
   return string


def whenever_clause(entity):
   return entity


def whenever_clause_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def disjunction_then_subject(then_subject):
   return then_subject


def disjunction_then_subject_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def cardinality(*args):
    value = ' '.join(args)
    if value == 'exactly one':
        return '1', '1'
    elif value == 'at least one':
        return '1', ''
    else:
        return '', '1'


def negation(*args):
   return True


def level(*args):
    value = ' '.join(args)
    if value == 'low':
        return '1'
    elif value == 'medium':
        return '2'
    else:
        return '3'


def constraint_body(entity):
   return entity


def constraint_body_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


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
    items_dict = {'equal to': '==', 'different from': '!=', 'lower than': '<', 'greater than': '>', 'lower than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def aggregate(aggregate_operator, string, entity):
    parameter_value = entity.fields[string]
    return Aggregate(aggregate_operator, [parameter_value], [entity])


def aggregate_operator(*args):
    value = ' '.join(args)
    if value == 'the number of':
        return 'count'
    elif value == 'the total of':
        return 'sum'
    elif value == 'the lowest value of':
        return 'min'
    else:
        return 'max'


def then_subject(entity):
   return entity


def then_object(then_subject):
   return then_subject


def then_object_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def comparison_operand(math):
   return math


def math_operand(entity):
   return entity


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def entity(negation, string, attribute):
    try:
        entity = Atom(CnlWizardCompiler.signatures[string])
        entity.negation = 'not ' if negation else ''
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def verb(string_1, attribute, string_2):
    name = string_1 + string_2
    try:
        entity = Atom(CnlWizardCompiler.signatures[name])
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def start(*propositions):
    res = ''
    for r in propositions:
        res += str(r) + '\n'
    return res
