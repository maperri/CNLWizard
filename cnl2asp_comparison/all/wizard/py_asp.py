from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*temporal_definition):
    raise NotImplementedError


def word(l_case, string):
    return f'{l_case}{string}'


def duration_clause(string):
    raise NotImplementedError


def whenever_then_clause_choice_ext(whenever_then_clause_choice, such_that_clause):
    raise NotImplementedError


def quantified_choice_proposition(quantified_choice, for_each):
    raise NotImplementedError


def compound_match_clause(*string):
    raise NotImplementedError


def simple_clause(simple_proposition):
    raise NotImplementedError


def positive_constraint(positive_constraint_body, terminal_clause):
    raise NotImplementedError


def negative_constraint(negative_constraint_body, terminal_clause):
    raise NotImplementedError


def preference_with_simple_proposition(level, simple_proposition, terminal_clause):
    raise NotImplementedError


def preference_with_math(level, math, terminal_clause):
    raise NotImplementedError


def proposition(whenever_then_clause_assignment):
    raise NotImplementedError


def such_that_clause(list_of_entities):
    raise NotImplementedError


def sum_string(*string):
    raise NotImplementedError


def diff_string(string, number):
    raise NotImplementedError


def math_first(equation):
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


def abs_eq(equation):
    raise NotImplementedError


def sum_eq(*equation):
    raise NotImplementedError


def diff_eq(equation_1, equation_2):
    raise NotImplementedError


def div_eq(equation_1, equation_2):
    raise NotImplementedError


def mult_eq(*equation):
    raise NotImplementedError


def par_eq(equation):
    raise NotImplementedError


def num_eq(number):
    raise NotImplementedError


def string_eq(string):
    raise NotImplementedError


def equation(abs_eq):
    raise NotImplementedError


def level(*args):
    raise NotImplementedError


def time_modifier(*args):
    raise NotImplementedError


def entity(word, label, time_modifier_1, attribute, negation, time_modifier_2, string, number):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def label(string, number):
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


def verb(negation, word_1, attribute, word_2):
    raise NotImplementedError


def inhead_verb(word_1, attribute, word_2):
    raise NotImplementedError


def attribute_value(string):
    raise NotImplementedError


def positive_constraint_body(comparison):
    raise NotImplementedError


def when_then_clause(simple_clause_1, simple_clause_2, simple_clause_3):
    raise NotImplementedError


def whenever_then_clause_choice(whenever_clauses, entity, subj_label, cardinality_1, inhead_verb, cardinality_2, list_of_entities):
    raise NotImplementedError


def whenever_then_clause_assignment(whenever_clauses, entity, subj_label, inhead_verb):
    raise NotImplementedError


def subj_label(label):
    raise NotImplementedError


def temporal_clause(entity, temporal_operator, time):
    raise NotImplementedError


def temporal_definition(string, date_1, time_1, number_1, date_2, time_2, number_2, number_3):
    raise NotImplementedError


def time(number_1, number_2, string):
    raise NotImplementedError


def date(number_1, number_2, number_3):
    raise NotImplementedError


def temporal_operator(*args):
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


def when_clause(simple_proposition):
    raise NotImplementedError


def between_where_clause(string_1, string_2, sum_string_1, diff_string_1, string_3, sum_string_2, diff_string_2):
    raise NotImplementedError


def negative_constraint_body(comparison):
    raise NotImplementedError


def comparison_first(math):
    raise NotImplementedError


def comparison_second(math):
    raise NotImplementedError


def linked_attribute(string_1, string_2, entity):
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


def negation(*args):
    return True


