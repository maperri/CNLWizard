import copy

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, Signature, create_var
from CNLWizard.libs.asp import Atom, Fact, Choice, Aggregate, Constraint, Comparison, WeakConstraint, Assignment


def start(*propositions):
    res = ''
    for signature in CnlWizardCompiler.signatures.values():
        if signature.type == 'temporal':
            atom = copy.deepcopy(signature)
            for i in range(signature.ub):
                atom.fields[list(atom.fields.keys())[0]] = str(i)
                res += str(Fact(Atom(atom))) + '\n'
    for name, value in CnlWizardCompiler.constants.items():
        if value:
            res += f'#const {name} = {value}.\n'
    for r in propositions:
        res += str(r) + '\n'
    return res

def entity(string, label, time_modifier, attribute, negation, time_modifier_last, modifier_value):
    if string in ["we", "I", "you"]:
        return ''
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    if label and not attribute:
        entity.fields[CnlWizardCompiler.signatures[string.lower().removesuffix('s')].keys[0]] = label
    if time_modifier == 'next':
        entity.fields['time'] = 'T+1'
    elif time_modifier == 'previous':
        entity.fields['time'] = 'T-1'
    if time_modifier_last and time_modifier_last == 'after':
        res = str(entity)
        operator = '>'
        if negation:
            operator = '<='
        res += f', T {operator} {modifier_value}'
        return res
    return entity

angles = set()
operations = []
def constant_definition(name, value):
    CnlWizardCompiler.constants[name] = value


def proposition(proposition):
    if operations:
        proposition.body.extend(operations)
    operations.clear()
    return proposition


def compounded_range_clause(name, start, end):
    CnlWizardCompiler.signatures[name] = name, [name + '_' + 'id'], [name + '_' + 'id'], None
    entity = Atom(CnlWizardCompiler.signatures[name.lower()])
    entity.fields[name + '_' + 'id'] = f'{start}..{end}'
    return Fact(entity)


def at_most(number):
    return '', number


def at_least(number):
    return number, ''


def between(first, second):
    return first, second


def exactly(number):
    return number, number


def cardinality(card):
    return card


def verb(string_1, attribute, string_2):
    name = string_1.lower()
    if string_2 and string_2 != "to":
        name += "_" + string_2
    entity = Signature(name, {})
    if name in CnlWizardCompiler.signatures:
        entity = Atom(CnlWizardCompiler.signatures[name])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def quantified_choice_proposition(quantified_choice, for_each):
    if for_each:
        for field, value in for_each.fields.items():
            quantified_choice.head.fields[field] = value
            CnlWizardCompiler.signatures[quantified_choice.head.name] = quantified_choice.head.name, quantified_choice.head.fields, quantified_choice.head.fields, None
        quantified_choice.body.append(for_each)
    return quantified_choice


def for_each(entity):
    return entity


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


def comparison_first(first):
    if first in angles:
        first = f'({first})\\360'
    return first


def comparison_second(second):
    if second in angles:
        second = f'({second})\\360'
    return second


def list_of_entities(*entities):
    if isinstance(entities, list):
        entities.append(entity)
        return entities
    return list(entities)


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def aggregate_operator(operator):
    return operator


def sum(arg):
    return 'sum'


def count(arg):
    return 'count'


def positive_constraint(positive_constraint_body, terminal_clause):
    res = Constraint(positive_constraint_body)
    if terminal_clause:
        res.body.extend(terminal_clause)
    return res


def positive_constraint_body(body):
    if isinstance(body, tuple):
        body[1].negate()
        body = list(body)
        return body
    else:
        body.negate()
    return [body]


def negative_constraint(negative_constraint_body, whenever_clause):
    res = Constraint(negative_constraint_body)
    if whenever_clause:
        res.body.extend(whenever_clause)
    return res


def attribute(name, attribute_value, comparison_operator, comparison_value):
    if "angle" in name:
        angles.add(attribute_value)
    if not attribute_value and comparison_operator == "equal to":
        attribute_value = comparison_value
    elif comparison_value:
        if not attribute_value:
            attribute_value = create_var()
        if "angle" in name:
            operations.append(Comparison(comparison_operator, [f'({attribute_value})\\360', f'({comparison_value})\\360']))
        else:
            operations.append(
                Comparison(comparison_operator, [attribute_value, comparison_value]))
    return [(name, attribute_value)]


def attribute_value(string):
    return string

def negative_constraint_body(body):
    if isinstance(body, tuple):
        body = list(body)
        return body
    return [body]


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


def where_clause_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def level(*args):
    value = ' '.join(args)
    if value == 'low':
        return '1'
    elif value == 'medium':
        return '2'
    else:
        return '3'


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math_first(string):
    return string

def math_second(string):
    return string

def preference(level, math, terminal_clause):
    new_var = create_var()
    if isinstance(math, Comparison) and math.operator in ['+', '-', '/', '*']:
        math = Comparison('=', [math, new_var])
    return WeakConstraint([math] + terminal_clause, new_var, level)


def terminal_clause(clause):
    if isinstance(clause, tuple):
        return list(clause)
    return [clause]


def comparison_where_clause(comparison):
    return comparison

def between_where_clause(label, first, second):
    return f'{first} <= {label}, {label} <= {second}'

def terminal_clause_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def sum_string(*string):
    return '+'.join(string)


def diff_string(*string):
    return '-'.join(string)


def simple_proposition_with_entities(entity_1, entity_2, entity_3):
    def set_fields(first, second):
        for field, value in second.fields.items():
            if field in first.fields:
                first.fields[field] = value
    for entity in entity_3:
        set_fields(entity_2, entity)
    set_fields(entity_2, entity_1)
    return entity_1, entity_2, *entity_3


def whenever_aggregate(aggregate):
    return aggregate


def when_clause(simple_proposition_with_entities):
    return simple_proposition_with_entities


def whenever_clauses(*entity):
    return list(entity)


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


def word(l_case, string):
    return f'{l_case}{string}'


def linked_attribute(string_1, string_2, entity):
    if "angle" in string_1:
        string_2 = f'({string_2})\\360'
    return string_2


def time_modifier(next):
    return next



def negation(*args):
    return True


def whenever_clause(negation, entity):
    if negation:
        entity.negation = 'not '
    return entity


def equation(*equation):
    return "".join(equation)

def whenever_then_clause_choice_ext(whenever_then_clause_choice, such_that_clause):
    if such_that_clause:
        whenever_then_clause_choice.condition += such_that_clause
    return whenever_then_clause_choice


def such_that_clause(list_of_entities):
    return list(list_of_entities)


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

def temporal_definition(string, start, end, number):
    if not number:
        number = 1
    res = []
    CnlWizardCompiler.signatures[string] = string, [f'id', 'value'], [f'id'], None
    elements = {}
    elements[start] = 0
    for i in range(int(start), int(end)):
        entity = CnlWizardCompiler.signatures[string]
        entity.fields[f'id'] = str(i)
        entity.fields[f'value'] = f'"{str(i)}"'
        res.append(Atom(entity))
    return '\n'.join(map(str, map(Fact, res)))


