from datetime import datetime, timedelta
from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, Signature, create_var
from CNLWizard.libs.asp import Atom, Fact, Choice, Aggregate, Constraint, Comparison, WeakConstraint, Assignment
import copy


labels = dict()
operations = []
time_elements = {}
date_elements = {}

def start(*propositions):
    res = ''
    for name, value in CnlWizardCompiler.constants.items():
        if value:
            res += f'#const {name} = {value}.\n'
    for r in range(len(propositions)):
        if r % 2 == 0:
            if propositions[r+1]:
                new_predicate = f'x{create_var()}'
                rule_copy = Assignment([copy.deepcopy(propositions[r].head)], propositions[r].body)
                rule_copy.head[0].fields['timeslot'] = f'{rule_copy.head[0].fields["timeslot"]}..{propositions[r+1]}'
                propositions[r].head.name = new_predicate
                rule_copy.body.append(propositions[r].head)
                res += str(rule_copy) + '\n'
            res += str(propositions[r]) + '\n'
    return res


def word(l_case, string):
    return f'{l_case}{string}'


def positive_constraint(positive_constraint_body, terminal_clause):
    res = Constraint(positive_constraint_body)
    if terminal_clause:
        res.body.extend(terminal_clause)
    return res


def preference(level, simple_clause, terminal_clause):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    set_fields(simple_clause[1], simple_clause[0])
    set_fields(simple_clause[1], terminal_clause[0])
    return WeakConstraint([simple_clause[0], simple_clause[1]] + terminal_clause, 1, level)


def proposition(proposition):
    labels.clear()
    if operations:
        proposition.body.extend(operations)
    operations.clear()
    return proposition


def sum_string(*string):
    return '+'.join(string)


def diff_string(*string):
    return '-'.join(string)


def math_first(string):
    return string

def math_second(string):
    return string


def level(*args):
    value = ' '.join(args)
    if value == 'low':
        return '1'
    elif value == 'medium':
        return '2'
    else:
        return '3'


def time_modifier(next):
    return next

def entity(string, label, attribute):
    if string.isupper() and string in labels:
        return labels[string]
    if string in ["we", "I", " you"]:
        return ''
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            if name == string:
                name = 'id'
            if name == 'id' and name not in entity.fields:
                name = f'{string}_{name}'
            if value in labels:
                for field, value in labels[value].fields.items():
                    if field in entity.fields:
                        entity.fields[field] = value
            else:
                entity.fields[name] = value
    if label:
        if entity.fields[CnlWizardCompiler.signatures[string.lower().removesuffix('s')].keys[0]] == '_':
            entity.fields[CnlWizardCompiler.signatures[string.lower().removesuffix('s')].keys[0]] = label
        if label in labels:
            prev = labels[label]
            for field, value in prev.fields.items():
                if value != '_':
                    entity.fields[field] = value
        labels[label] = entity
    return entity


def positive_constraint_body(body):
    if isinstance(body, tuple):
        body[1].negate()
        body = list(body)
        return body
    else:
        body.negate()
    return [body]


def comparison_first(first):
    return first


def comparison_second(second):
    return second


def linked_attribute(string_1, string_2, entity):
    if not string_2:
        string_2 = create_var()
        entity.fields[string_1] = string_2
    return string_2


def verb(string_1, attribute, string_2):
    name = string_1.lower()
    if string_2 and string_2 != "to":
        name += "_" + string_2
    entity = Signature(name, {})
    if name in CnlWizardCompiler.signatures:
        entity = Atom(CnlWizardCompiler.signatures[name])
    if attribute:
        for name, value in attribute:
            if value in labels:
                for field, value in labels[value].fields.items():
                    entity.fields[field] = value
            else:
                entity.fields[name] = value
    return entity


def at_most(number):
    return None, number


def at_least(number):
    return number, None


def between(first, second):
    return first, second


def exactly(number):
    return number, number


def list_of_entities(*entities):
    if isinstance(entities, list):
        entities.append(entity)
        return entities
    return list(entities)


def aggregate_operator(operator):
    return operator


def whenever_clause(negation, entity):
    if negation:
        entity.negation = 'not '
    return entity


def whenever_clauses(*entity):
    return list(entity)


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def comparison_operator(*args):
    items_dict = {'equal to': '==',
                  'different from': '!=',
                  'less than': '<',
                  'greater than': '>',
                  'less than or equal to': '<=',
                  'greater than or equal to': '>=',
                  'at most': '<'}
    item = ' '.join(args)
    return items_dict[item]



def sum(arg):
    return 'sum'


def count(arg):
    return 'count'


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    operands = []
    for operand in args[1:]:
        if isinstance(operand, list):
            operands.extend(operand)
        else:
            operands.append(operand)
    return Comparison(operator, operands)


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def simple_proposition(entity_1, entity_2, entity_3):
    return entity_1, entity_2, entity_3


def attribute(name, attribute_value, comparison_operator, comparison_value):
    if not attribute_value and comparison_operator == "equal to":
        attribute_value = comparison_value
    elif not attribute_value and comparison_value:
        attribute_value = create_var()
        operations.append(Comparison(comparison_operator, [attribute_value, comparison_value]))
    return [(name, attribute_value)]


def whenever_then_clause_choice(whenever_clauses, entity, cardinality_1, verb, cardinality_2, list_of_entities):
    def set_fields(first, second):
        for field in second.fields.keys():
            if field in first.fields:
                if (first.fields[field] != '_' and second.fields[field] != '_') or (first.name == second.name and first.fields[field] == second.fields[field]):
                    continue
                if second.fields[field] == '_':
                    second.fields[field] = create_var()
                first.fields[field] = second.fields[field]
            elif field == first.name:
                if second.fields[field] == '_':
                    second.fields[field] = create_var()
                first.fields['id'] = second.fields[field]
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
    for entity in list_of_entities + body:
        set_fields(entity, res)
        set_fields(res, entity)
    return Choice(res, body, list_of_entities, cardinality[0], cardinality[1])


def negation(*args):
    return True


def cardinality(card):
    return card


def attribute_value(string):
    return string

def attribute_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def math_first_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def active_aggregate(aggregate_operator, string, verb, list_of_entities):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
            if field == 'id' and second.name in first.fields:
                first.fields[second.name] = value
    discriminant_var = create_var()
    verb.fields[string] = discriminant_var
    for entity in list_of_entities:
        set_fields(verb, entity)
    return Aggregate(aggregate_operator, [discriminant_var], [verb] + list_of_entities)


def temporal_clause(entity, temporal_operator, time):
    var = create_var()
    entity.fields["id"] = var
    if temporal_operator == "after":
        operator = ">"
    else:
        operator = "<"
    return Comparison(operator, [var, time_elements[time]])


def time(number_1, number_2, string):
    return datetime.strptime(f'{number_1}:{number_2} {string}', '%I:%M %p')


def temporal_operator(op):
    return op


def date(number_1, number_2, number_3):
    return datetime.strptime(f'{number_1}/{number_2}/{number_3}', '%d/%m/%Y')


def temporal_definition(string, start, end, number):
    if not number:
        number = 1
    res = []
    CnlWizardCompiler.signatures[string] = string, [f'id', 'value'], [f'id'], None
    elements = {}
    elements[start] = 0
    if start > datetime.strptime(f'02/01/1900', '%d/%m/%Y'):
        delta = timedelta(days=int(number))
        format = '%d/%m/%Y'
    else:
        delta = timedelta(minutes=int(number))
        format = '%I:%M %p'
    entity = CnlWizardCompiler.signatures[string]
    entity.fields[f'{string}_id'] = str(0)
    entity.fields[f'value'] = f'"{str(start.strftime(format))}"'
    res.append(Atom(entity))
    start = start + delta
    counter = 1
    while start < end:
        entity = CnlWizardCompiler.signatures[string]
        entity.fields[f'{string}_id'] = str(counter)
        entity.fields[f'value'] = f'"{str(start.strftime(format))}"'
        res.append(Atom(entity))
        if start > end:
            start = end
        elements[start] = counter
        counter += 1
        start = start + delta
    global time_elements
    time_elements = elements
    return '\n'.join(map(str, map(Fact, res)))


def duration_clause(string):
    return string


