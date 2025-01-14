from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*propositions):
    raise NotImplementedError


def constraint(comparison):
    raise NotImplementedError


def propositions(constraint):
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


def entity(string, attribute):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def there_is_clause(entity):
    raise NotImplementedError


