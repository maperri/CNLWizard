from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*propositions):
    raise NotImplementedError


def there_is_clause(entity):
    raise NotImplementedError


def propositions(there_is_clause):
    raise NotImplementedError


def preferred_that(*args):
    raise NotImplementedError


def constant(string, attribute_value):
    raise NotImplementedError


def constraint(constraint_body, whenever_clause):
    raise NotImplementedError


def whenever_then_clause_choice(whenever_clause, cardinality, disjunction_then_subject, then_object):
    raise NotImplementedError


def whenever_then_clause_assignment(whenever_clause, then_subject):
    raise NotImplementedError


def weak_constraint(level, comparison, whenever_clause):
    raise NotImplementedError


def heuristic(sign_heuristic_clause):
    raise NotImplementedError


def attribute_value(string):
    raise NotImplementedError


def whenever_clause(entity):
    raise NotImplementedError


def whenever_clause_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def disjunction_then_subject(then_subject):
    raise NotImplementedError


def disjunction_then_subject_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def cardinality(*args):
    raise NotImplementedError


def negation(*args):
    raise NotImplementedError


def level(*args):
    raise NotImplementedError


def constraint_body(entity):
    raise NotImplementedError


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
    raise NotImplementedError


def aggregate_operator(*args):
    raise NotImplementedError


def then_subject(entity):
    raise NotImplementedError


def then_object(then_subject):
    raise NotImplementedError


def then_object_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def comparison_operand(math):
    raise NotImplementedError


def math_operand(entity):
    raise NotImplementedError


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
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def verb(string_1, attribute, string_2):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def sign_heuristic_clause(if_clause, preferred_that, entity, heur_negation, heur_priority):
    raise NotImplementedError


def level_heuristic_clause(if_clause, entity, heur_level, heur_priority):
    raise NotImplementedError


def true_false_heuristic_clause(if_clause, entity, heur_negation, heur_level, heur_priority):
    raise NotImplementedError


def if_clause(entity):
    raise NotImplementedError


def if_clause_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def heur_negation(*args):
    raise NotImplementedError


def heur_level(*args):
    raise NotImplementedError


def heur_priority(number):
    raise NotImplementedError


