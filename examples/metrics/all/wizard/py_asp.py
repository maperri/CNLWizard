from datetime import datetime, timedelta
from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, Signature, create_var
from CNLWizard.libs.asp import Atom, Fact, Choice, Aggregate, Constraint, Comparison, WeakConstraint, Assignment
import copy

labels = dict()
angles = set()
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
                rule_copy.head[0].fields['timeslot_id'] = f'{rule_copy.head[0].fields["timeslot_id"]}..{propositions[r+1]}'
                propositions[r].head.name = new_predicate
                rule_copy.body.append(propositions[r].head)
                res += str(rule_copy) + '\n'
            if propositions[r]:
                res += str(propositions[r]) + '\n'
    return res


def word(l_case, string):
    return f'{l_case}{string}'


def positive_constraint(positive_constraint_body, terminal_clause):
    res = Constraint(positive_constraint_body)
    if terminal_clause:
        res.body.extend(terminal_clause)
    return res


def proposition(proposition):
    labels.clear()
    if isinstance(proposition, Atom):
        proposition = Fact(proposition)
    if operations:
        aggregates = {}
        for elem in proposition.body:
            if isinstance(elem, Comparison) and isinstance(elem.operands[0], str) and elem.operands[0].endswith('}'):
                aggregates[elem.operands[0].split('{')[1].split(':')[0]] = elem.operands
        for operation in operations:
            if operation.operands[0] in aggregates:
                aggregates[operation.operands[0]][0] = aggregates[operation.operands[0]][0].removesuffix('}') + ', ' + str(operation) + '}'
                continue
            if operation.operands[1] in aggregates:
                aggregates[operation.operands[1]][0] = aggregates[operation.operands[1]][0].removesuffix('}') + ', ' + str(operation) + '}'
                continue
            proposition.body.append(operation)
    operations.clear()
    return proposition

def subj_label(label):
    if label in labels:
        return labels[label]
    return label

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

def entity(string, label, time_modifier, attribute, negation, time_modifier_last, modifier_value):
    if string.isupper() and string in labels:
        return labels[string]
    if string in ["we", "I", " you"]:
        return ''
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            if value in labels and labels[value].name == name and name not in entity.fields:
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
    if time_modifier == 'next':
        entity.fields['time'] = 'T+1'
    elif time_modifier == 'previous':
        entity.fields['time'] = 'T-1'
    if time_modifier_last and time_modifier_last == 'after ':
        res = str(entity)
        operator = '>'
        if negation:
            operator = '<='
        res += f', T {operator} {modifier_value}'
        return res
    return entity


def positive_constraint_body(body):
    if isinstance(body, tuple):
        body[1].negate()
        body = list(body)
        return body
    else:
        if hasattr(body, 'negate'):
            body.negate()
    return [body]


def comparison_first(first):
    if first in angles:
        first = f'({first})\\360'
    return first


def comparison_second(second):
    if second in angles:
        second = f'({second})\\360'
    return second


def linked_attribute(string_1, string_2, entity):
    if "angle" in string_1:
        string_2 = f'({string_2})\\360'
    if not string_2:
        string_2 = create_var()
        entity.fields[string_1] = string_2
    return string_2


def verb(negation, string_1, attribute, string_2):
    name = string_1.lower().removesuffix('s')
    if string_2 and string_2 != "to":
        name += "_" + string_2
    entity = Signature(name, {})
    if name in CnlWizardCompiler.signatures:
        entity = Atom(CnlWizardCompiler.signatures[name])
    if attribute:
        for name, value in attribute:
            if value in labels and name not in entity.fields:
                for field, value in labels[value].fields.items():
                    entity.fields[field] = value
            else:
                entity.fields[name] = value
    return entity


def at_most(number):
    return '', number


def at_least(number):
    return number, ''


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
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value

    for entity in entity_3:
        set_fields(entity_2, entity)
    set_fields(entity_2, entity_1)
    return entity_1, entity_2, *entity_3

def simple_clause(args):
    entity_1 = args[0]
    verb = args[1]
    entity_2 = args[2]
    if not verb.fields:
        fields = []
        for field in entity_1.fields:
            fields.append(field)
        for field in entity_2.fields:
            fields.append(field)
        CnlWizardCompiler.signatures[verb.name] = verb.name, fields, fields, [None, None, None]
    for key, value in entity_1.fields.items():
        verb.fields[key] = str(value)
    for key, value in entity_2.fields.items():
        if key in verb.fields and verb.fields[key] == value:
            continue
        elif key in verb.fields and verb.fields[key] != '_':
            verb.fields[key] += ',' + str(value)
        else:
            verb.fields[key] = str(value)
    return verb

def attribute(name, attribute_value, comparison_operator, comparison_value):
    if "angle" in name:
        angles.add(attribute_value)
    if not attribute_value and comparison_operator == "equal to":
        attribute_value = comparison_value
    elif comparison_value:
        if not attribute_value:
            attribute_value = create_var()
        if comparison_value.isalpha() and comparison_value not in CnlWizardCompiler.constants and not comparison_value[0].isupper():
            comparison_value = f'"{comparison_value}"'
        if "angle" in name:
            operations.append(
                Comparison(comparison_operator, [f'({attribute_value})\\360', f'({comparison_value})\\360']))
        else:
            operations.append(
                Comparison(comparison_operator, [attribute_value, comparison_value]))
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
    list_of_entities = [] if not list_of_entities else list_of_entities
    for entity in list_of_entities + body:
        if not isinstance(entity, str):
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
    discriminant_var = create_var()
    verb.fields[string] = discriminant_var
    for entity in list_of_entities:
        set_fields(verb, entity)
    return Aggregate(aggregate_operator, [discriminant_var], [verb] + list_of_entities)


def temporal_clause(entity, temporal_operator, time):
    var = create_var()
    entity.fields["timeslot_id"] = var
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
    CnlWizardCompiler.signatures[string] = string, [f'{string}_id', 'value'], [f'{string}_id'], None
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


def compounded_range_clause(name, start, end):
    CnlWizardCompiler.signatures[name] = name, [name + '_' + 'id'], [name + '_' + 'id'], None
    entity = Atom(CnlWizardCompiler.signatures[name.lower()])
    entity.fields[name + '_' + 'id'] = f'{start}..{end}'
    return Fact(entity)


def constant_definition(name, value):
    CnlWizardCompiler.constants[name] = value


def quantified_choice_proposition(quantified_choice, for_each):
    if for_each:
        for field, value in for_each.fields.items():
            quantified_choice.head.fields[field] = value
            CnlWizardCompiler.signatures[quantified_choice.head.name] = quantified_choice.head.name, quantified_choice.head.fields, quantified_choice.head.fields, None
        quantified_choice.body.append(for_each)
    return quantified_choice


def for_each(entity):
    return entity


def is_initialized(atom):
    for field in atom.fields.values():
        if field != '_':
            return True
    return False

def initialize_entity(entity):
    if not is_initialized(entity):
        for field in entity.fields.keys():
            entity.fields[field] = create_var()

def quantified_choice(subj, verb, cardinality, obj):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    initialize_entity(subj)
    initialize_entity(obj)
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


def simple_aggregate(aggregate_operator, discriminant, discriminant_var, verb, list_of_entities):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    discriminant = discriminant.removesuffix('s')
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


def negative_constraint(negative_constraint_body, whenever_clause):
    res = Constraint(negative_constraint_body)
    if whenever_clause:
        res.body.extend(whenever_clause)
    return res


def negative_constraint_body(body):
    if isinstance(body, tuple):
        body = list(body)
        return body
    return [body]


def terminal_clause(clause):
    if isinstance(clause, tuple):
        return list(clause)
    return [clause]


def terminal_clause_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def between_where_clause(label, first, second):
    operations.append(Comparison('<=', [first, label]))
    operations.append(Comparison('<=', [label, second]))
    return


def when_clause(simple_proposition):
    return simple_proposition


def comparison_where_clause(comparison):
    return comparison


def whenever_aggregate(aggregate):
    return aggregate


def preference_with_simple_proposition(level, simple_proposition, terminal_clause):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value

    set_fields(simple_proposition[1], simple_proposition[0])
    set_fields(simple_proposition[1], terminal_clause[0])
    return WeakConstraint([simple_proposition[0], simple_proposition[1]] + terminal_clause, 1, level)


def preference_with_math(level, math, where_clause):
    new_var = create_var()
    if isinstance(math, Comparison) and math.operator in ['+', '-', '/', '*']:
        math = Comparison('=', [math, new_var])
    return WeakConstraint([math] + where_clause, new_var, level)


def label(*string):
    res = ''
    for s in string:
        if s:
            res += s
    return res


def whenever_then_clause_choice_ext(whenever_then_clause_choice, such_that_clause):
    if such_that_clause:
        whenever_then_clause_choice.condition += such_that_clause
    return whenever_then_clause_choice


def whenever_then_clause_assignment(whenever_clauses, entity, verb):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value

    body = whenever_clauses
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


def such_that_clause(list_of_entities):
    return list(list_of_entities)


def inhead_verb(word_1, attribute, word_2):
    return verb(False, word_1, attribute, word_2)


def abs_eq(equation):
    return f'|{equation}|'


def sum_eq(*equation):
    return '+'.join(equation)


def diff_eq(equation_1, equation_2):
    return f'{equation_1}-{equation_2}'


def div_eq(equation_1, equation_2):
    return f'{equation_1}/{equation_2}'


def mult_eq(*equation):
    return '*'.join(equation)


def par_eq(equation):
    return f'({equation})'


def num_eq(number):
    return number


def string_eq(string):
    return string


def equation(*equation):
    return "".join(equation)


def compound_match_clause(*string):
    CnlWizardCompiler.signatures[string[0]] = string[0], ['id'], ['id'], [None, None, None]
    res = []
    for v in string[1:]:
        atom = CnlWizardCompiler.signatures[string[0]]
        atom.fields['id'] = f'"{v}"'
        res.append(atom)
    return '. '.join(map(str, res)) + '.'


def when_then_clause(simple_proposition_1, simple_proposition_2, simple_proposition_3):
    return ', '.join([str(simple_proposition_1), str(simple_proposition_2), str(simple_proposition_3)])


def positive_constraint_body_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


