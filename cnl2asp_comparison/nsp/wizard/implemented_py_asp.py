from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, Signature, create_var
from CNLWizard.libs.asp import Atom, Fact, Choice, Aggregate, Constraint, Comparison, WeakConstraint

labels = dict()
operations = []

def start(*propositions):
    res = ''
    for name, value in CnlWizardCompiler.constants.items():
        if value:
            res += f'#const {name} = {value}.\n'
    for r in propositions:
        res += str(r) + '\n'
    return res


def attribute(name, attribute_value, comparison_operator, comparison_value):
    if not attribute_value and comparison_operator == "equal to":
        attribute_value = comparison_value
    elif not attribute_value and comparison_value:
        attribute_value = create_var()
        if comparison_value.isalpha() and comparison_value not in CnlWizardCompiler.constants and not comparison_value[0].isupper():
            comparison_value = f'"{comparison_value}"'
        operations.append(Comparison(comparison_operator, [attribute_value, comparison_value]))
    return [(name, attribute_value)]

def negation(*args):
    return True

def constant_definition(name, value):
    CnlWizardCompiler.constants[name] = value


def proposition(proposition):
    labels.clear()
    if operations:
        aggregates = {}
        for elem in proposition.body:
            if isinstance(elem, Comparison) and isinstance(elem.operands[0], str) and elem.operands[0].endswith('}'):
                aggregates[elem.operands[0].split('{')[1].split(':')[0]] = elem.operands
        for operation in operations:
            if operation.operands[0] in aggregates:
                aggregates[operation.operands[0]][0] = aggregates[operation.operands[0]][0].removesuffix('}') + ', ' + str(operation) + '}'
                break
            if operation.operands[1] in aggregates:
                aggregates[operation.operands[1]][0] = aggregates[operation.operands[1]][0].removesuffix('}') + ', ' + str(operation) + '}'
                break
            proposition.body.append(operation)
    operations.clear()
    return proposition

def compounded_range_clause(name, start, end):
    CnlWizardCompiler.signatures[name] = name, [name + '_' + 'id'], [name + '_' + 'id'], None
    entity = Atom(CnlWizardCompiler.signatures[name.lower()])
    entity.fields[name + '_' + 'id'] = f'{start}..{end}'
    return Fact(entity)


def at_most(number):
    return None, number


def at_least(number):
    return number, None


def between(first, second):
    return first, second


def exactly(number):
    return number, number


def cardinality(card):
    return card


def verb(string_1, attribute, string_2):
    name = string_1.lower().removesuffix('s')
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


def comparison_first(aggregate):
    return aggregate


def comparison_second(number):
    return number


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


def whenever_clause(negation, entity):
    if negation:
        entity.negation = 'not '
    return entity


def sum(arg):
    return 'sum'


def count(arg):
    return 'count'


def positive_constraint(positive_constraint_body, whenever_clause):
    res = Constraint(positive_constraint_body)
    if whenever_clause:
        res.body.extend(whenever_clause)
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


def negative_constraint_body(body):
    if isinstance(body, tuple):
        body = list(body)
        return body
    return [body]


def simple_aggregate(aggregate_operator, discriminant, discriminant_var, verb, list_of_entities):
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

def preference(level, math, where_clause):
    new_var = create_var()
    if isinstance(math, Comparison) and math.operator in ['+', '-', '/', '*']:
        math = Comparison('=', [math, new_var])
    return WeakConstraint([math] + where_clause, new_var, level)


def terminal_clause(clause):
    if isinstance(clause, tuple):
        return list(clause)
    return [clause]


def comparison_where_clause(comparison):
    return comparison

def between_where_clause(label, first, second):
    operations.append(Comparison('<=', [first, label]))
    operations.append(Comparison('<=', [label, second]))
    return

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


def word(l_case, string):
    return f'{l_case}{string}'


def attribute_value(string):
    return string



def entity(string, attribute):
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            if name == string:
                name = 'id'
            if name == 'id' and name not in entity.fields:
                name = f'{string}_{name}'
            entity.fields[name] = value
    return entity


