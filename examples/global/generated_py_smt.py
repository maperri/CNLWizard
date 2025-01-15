from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*propositions):
    raise NotImplementedError


def function_definition(string_1, string_2, string_3):
    raise NotImplementedError


def constraint(clause_body):
    raise NotImplementedError


def if_then(clause_body_1, clause_body_2):
    raise NotImplementedError


def propositions(function_definition):
    raise NotImplementedError


def simple_clause(entity_1, negation, entity_2):
    raise NotImplementedError


def negation(*args):
    raise NotImplementedError


def math_operator(*args):
    items_dict = {'sum': '''+''', 'difference': '''-''', 'division': '''/''', 'multiplication': '''*'''}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def comparison_operator(*args):
    items_dict = {'equal to': '''==''', 'different from': '''!=''', 'lower than': '''<''', 'greater than': '''>''', 'lower than or equal to': '''<=''', 'greater than or equal to': '''>='''}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def conjunction(*args):
    raise NotImplementedError


def disjunction(*args):
    raise NotImplementedError


def implication(*args):
    raise NotImplementedError


def equivalence(*args):
    raise NotImplementedError


def negation_op(*args):
    raise NotImplementedError


def formula_operator(*args):
    items_dict = {'and': conjunction(*args), 'or': disjunction(*args), 'imply': implication(*args), 'implies': implication(*args), 'is equivalent to': equivalence(*args), 'not': negation_op(*args)}
    item = ' '.join(args)
    return items_dict[item]


def formula(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator(*args)


def clause_body(there_is_clause):
    raise NotImplementedError


def comparison_operand(math):
    raise NotImplementedError


def math_operand(entity):
    raise NotImplementedError


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def attributes(*attribute):
    raise NotImplementedError


def entity(string, attributes):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def there_is_clause(entity):
    raise NotImplementedError


