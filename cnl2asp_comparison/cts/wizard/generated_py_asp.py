from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*temporal_definition):
    raise NotImplementedError


def word(l_case, string):
    return f'{l_case}{string}'


def duration_clause(string):
    raise NotImplementedError


def positive_constraint(positive_constraint_body, whenever_clauses):
    raise NotImplementedError


def preference(level, simple_proposition, whenever_clauses):
    raise NotImplementedError


def proposition(whenever_then_clause_choice):
    raise NotImplementedError


def sum_string(*string):
    raise NotImplementedError


def diff_string(string, number):
    raise NotImplementedError


def math_first(string):
    raise NotImplementedError


def math_first_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def math_second(string):
    raise NotImplementedError


def level(*args):
    raise NotImplementedError


def entity(string_1, string_2, attribute):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def attribute(string, attribute_value_1, comparison_operator, attribute_value_2):
    raise NotImplementedError


def attribute_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def attribute_value(string):
    raise NotImplementedError


def positive_constraint_body(comparison):
    raise NotImplementedError


def temporal_clause(entity, temporal_operator, time):
    raise NotImplementedError


def temporal_definition(string, date_1, time_1, date_2, time_2, number):
    raise NotImplementedError


def time(number_1, number_2, string):
    raise NotImplementedError


def date(number_1, number_2, number_3):
    raise NotImplementedError


def temporal_operator(*args):
    raise NotImplementedError


def comparison_first(math):
    raise NotImplementedError


def comparison_second(number):
    raise NotImplementedError


def linked_attribute(string_1, string_2, entity):
    raise NotImplementedError


def cardinality(card):
    return card


def verb(string_1, attribute, string_2):
    name = string_1.lower() + "_" + string_2
    entity = Signature(name, {})
    if name in CnlWizardCompiler.signatures:
        entity = Atom(CnlWizardCompiler.signatures[name])
    if attribute:
        for name, value in attribute:
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
    items_dict = {'equal to': '!=',
                  'different from': '==',
                  'less than': '>=',
                  'greater than': '<=',
                  'less than or equal to': '>',
                  'greater than or equal to': '<',
                  'at most': '<='}
    item = ' '.join(args)
    return items_dict[item]


def sum(arg):
    return 'sum'


def count(arg):
    return 'count'


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


def simple_proposition(entity_1, entity_2, entity_3):
    return entity_1, entity_2, entity_3


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


def aggregate_operator(operator):
    return operator


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


def negation(*args):
    return True


