from numpy.core.defchararray import isalpha, isupper
from sympy import discriminant

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, Signature, create_var


class Atom:
    def __init__(self, entity):
        self.name: str = entity.name
        self.fields: dict = entity.fields
        self.negation: str = ''

    def negate(self):
        self.negation = 'not ' if not self.negation else ''

    def __str__(self):
        values = []
        for value in self.fields.values():
            if value != '_' and isalpha(value) and value not in CnlWizardCompiler.constants and not isupper(value[0]):
                values.append(f'"{value}"')
            else:
                values.append(value)
        return f'{self.negation}{self.name}({",".join(values)})'


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
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return f':- {", ".join(map(str, self.body))}.'


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
        if not condition:
            condition = []
        self.condition: list = condition
        self.lb: str = lb
        self.ub: str = ub

    def __str__(self):
        head_cond = ": " + ", ".join(map(str, self.condition)) if self.condition else ''
        return f'{self.lb} {{{self.head}{head_cond}}} {self.ub} :- {", ".join(map(str, self.body))}.'


class Comparison:
    def __init__(self, operator, operands):
        self.operator: str = operator
        self.operands: list = operands

    def negate(self):
        negation = {'>': '<=',
                    '<': '>=',
                    '>=': '<',
                    '<=': '>',
                    '==': '!=',
                    '!=': '=='}
        self.operator = negation[self.operator]

    def __str__(self):
        return f'{self.operator.join(map(str, self.operands))}'

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
    name = string_1.lower() + "_" + string_2
    entity = Signature(name, {})
    if name in CnlWizardCompiler.signatures:
        entity = Atom(CnlWizardCompiler.signatures[name])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def comparison_operator(*args):
    items_dict = {'equal to': '!=',
                  'different from': '==',
                  'less than': '>=',
                  'greater than': '<=',
                  'less than or equal to': '>',
                  'greater than or equal to': '<',
                  'at most': '<='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def simple_proposition(entity_1, entity_2, entity_3):
    return entity_1, entity_2, entity_3


def negated_simple_proposition(entity_1, entity_2, entity_3):
    entity_2.negation = 'not '
    return entity_1, entity_2, entity_3

def constant_definition(name, value):
    CnlWizardCompiler.constants[name] = value

def compounded_range_clause(name, start, end):
    CnlWizardCompiler.signatures[name] = name, ['id'], ['id'], None
    entity = Atom(CnlWizardCompiler.signatures[name.lower()])
    entity.fields['id'] = f'{start}..{end}'
    return Fact(entity)

def exactly(number):
    return number, number


def at_most(number):
    return None, number


def at_least(number):
    return number, None


def between(first, second):
    return first, second


def cardinality(card):
    return card


def quantified_choice(subj, verb, cardinality, obj):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    if verb.name not in CnlWizardCompiler.signatures:
        fields = list(verb.fields.keys())
        fields += CnlWizardCompiler.signatures[subj.name].keys
        fields += CnlWizardCompiler.signatures[obj.name].keys
        CnlWizardCompiler.signatures[verb.name] = verb.name, fields, fields, None
    res = CnlWizardCompiler.signatures[verb.name]
    set_fields(res, verb)
    set_fields(res, subj)
    set_fields(res, obj)
    return Choice(res, [subj], [obj], cardinality[0], cardinality[1])


def quantified_assignment(subj, verb, obj):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value

    if verb.name not in CnlWizardCompiler.signatures:
        fields = list(verb.fields.keys())
        fields += CnlWizardCompiler.signatures[subj.name].keys
        fields += CnlWizardCompiler.signatures[obj.name].keys
        CnlWizardCompiler.signatures[verb.name] = verb.name, fields, fields, None
    res = CnlWizardCompiler.signatures[verb.name]
    set_fields(res, verb)
    set_fields(res, subj)
    set_fields(res, obj)
    return Assignment(verb, [subj], [obj])


def aggregate_operator(operator):
    return operator


def count(arg):
    return 'count'


def sum(arg):
    return 'sum'


def list_of_entities(*entities):
    if isinstance(entities, list):
        entities.append(entity)
        return entities
    return list(entities)


def simple_aggregate(aggregate_operator, discriminant, discriminant_var, verb, list_of_entities):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    if not discriminant_var:
        discriminant_var = create_var()
    if discriminant in CnlWizardCompiler.signatures:
        discriminant = CnlWizardCompiler.signatures[discriminant].keys[0]
    verb.fields[discriminant] = discriminant_var
    for entity in list_of_entities:
        set_fields(verb, entity)
    list_of_entities.append(verb)
    return Aggregate(aggregate_operator, [discriminant_var], list_of_entities)


def passive_aggregate(aggregate_operator, discriminant, discriminant_var, discriminant_set, subj,  verb, obj):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    if not discriminant_var:
        discriminant_var = create_var()
    discriminant_set_var = create_var()
    if discriminant in CnlWizardCompiler.signatures:
        discriminant = CnlWizardCompiler.signatures[discriminant].keys[0]
    if discriminant_set in CnlWizardCompiler.signatures:
        discriminant_set = CnlWizardCompiler.signatures[discriminant_set].keys[0]
    if obj and discriminant in obj.fields:
        obj.fields[discriminant] = discriminant_var
    if discriminant in verb.fields:
        verb.fields[discriminant] = discriminant_var
    if obj and discriminant_set in obj.fields:
        obj.fields[discriminant_set] = discriminant_set_var
    if discriminant_set in verb.fields:
        verb.fields[discriminant_set] = discriminant_set_var
    if obj:
        set_fields(verb, obj)
    for field in subj.fields:
        if field in verb.fields:
            subj.fields[field] = create_var()
            verb.fields[field] = subj.fields[field]
    discriminant = [discriminant_var, discriminant_set_var] if discriminant_set else [discriminant_var]
    body = [obj, verb] if obj else [verb]
    return str(subj) + ', ' + str(Aggregate(aggregate_operator, discriminant, body))

def whenever_clause(negation, entity):
    if negation:
        entity.negation = 'not '
    return entity


def whenever_clauses(*entity):
    return list(entity)


def whenever_then_clause_choice(whenever_clauses, entity, cardinality_1, verb, cardinality_2, list_of_entities):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    body = whenever_clauses
    cardinality = cardinality_1 if cardinality_1 else cardinality_2
    if verb.name not in CnlWizardCompiler.signatures:
        fields = list(verb.fields.keys())
        if entity:
            fields += CnlWizardCompiler.signatures[entity.name].keys
        CnlWizardCompiler.signatures[verb.name] = verb.name, fields, fields, None
    res = CnlWizardCompiler.signatures[verb.name]
    set_fields(res, verb)
    if entity:
        set_fields(res, entity)
    return Choice(res, body, list_of_entities, cardinality[0], cardinality[1])



def whenever_then_clause_assignment(whenever_clauses, entity, verb):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value

    body = whenever_clauses
    if list_of_entities:
        body += list_of_entities
    if verb.name not in CnlWizardCompiler.signatures:
        fields = list(verb.fields.keys())
        if entity:
            fields += CnlWizardCompiler.signatures[entity.name].keys
        CnlWizardCompiler.signatures[verb.name] = verb.name, fields, fields, None
    res = CnlWizardCompiler.signatures[verb.name]
    set_fields(res, verb)
    if entity:
        set_fields(res, entity)
    return Assignment([res], body)

def negation(*args):
    return True


def active_aggregate(aggregate_operator, string, verb, list_of_entities):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    discriminant_var = create_var()
    verb.fields[string] = discriminant_var
    for entity in list_of_entities:
        set_fields(verb, entity)
    return Aggregate(aggregate_operator, [discriminant_var], [verb] + list_of_entities)
