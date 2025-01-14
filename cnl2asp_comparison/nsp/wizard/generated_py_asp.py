from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*proposition):
    raise NotImplementedError


def word(l_case, string):
    return f'{l_case}{string}'


def quantified_choice_proposition(quantified_choice, for_each):
    raise NotImplementedError


def positive_constraint(positive_constraint_body, terminal_clause):
    raise NotImplementedError


def negative_constraint(negative_constraint_body, terminal_clause):
    raise NotImplementedError


def preference(level, math, terminal_clause):
    raise NotImplementedError


def proposition(constant_definition):
    raise NotImplementedError


def attribute(string, attribute_value_1, comparison_operator, attribute_value_2):
    raise NotImplementedError


def attribute_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def verb(word_1, attribute, word_2):
    raise NotImplementedError


def attribute_value(string):
    raise NotImplementedError


def when_clause(simple_proposition_with_entities):
    raise NotImplementedError


def terminal_clause(comparison_where_clause):
    raise NotImplementedError


def terminal_clause_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def whenever_aggregate(comparison):
    raise NotImplementedError


def comparison_where_clause(comparison):
    raise NotImplementedError


def between_where_clause(string_1, string_2, sum_string_1, diff_string_1, string_3, sum_string_2, diff_string_2):
    raise NotImplementedError


def sum_string(*string):
    raise NotImplementedError


def diff_string(string, number):
    raise NotImplementedError


def math_first(string):
    raise NotImplementedError


def math_second(string):
    raise NotImplementedError


def level(*args):
    raise NotImplementedError


def positive_constraint_body(comparison):
    raise NotImplementedError


def negative_constraint_body(comparison):
    raise NotImplementedError


def comparison_first(simple_aggregate):
    raise NotImplementedError


def comparison_second(number):
    raise NotImplementedError


def for_each(entity):
    raise NotImplementedError


def constant_definition(name, value):
    CnlWizardCompiler.constants[name] = value


def compounded_range_clause(name, start, end):
    CnlWizardCompiler.signatures[name] = name, ['id'], ['id'], None
    entity = Atom(CnlWizardCompiler.signatures[name.lower()])
    entity.fields['id'] = f'{start}..{end}'
    return Fact(entity)


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


def cardinality(card):
    return card


def entity(string, attribute):
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
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


def simple_proposition_with_entities(entity_1, entity_2, entity_3):
    return entity_1, entity_2, entity_3


def negation(*args):
    return True


