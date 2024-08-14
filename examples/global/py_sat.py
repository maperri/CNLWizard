from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*propositions):
    raise NotImplementedError


def constraint(clause_body):
    raise NotImplementedError


def if_then(clause_body_1, clause_body_2):
    raise NotImplementedError


def propositions(constraint):
    raise NotImplementedError


def simple_clause(entity_1, negation, entity_2):
    raise NotImplementedError


def negation(*args):
    raise NotImplementedError


def formula_operator(*args):
    items_dict = {'and': '&', 'or': '|', 'imply': '>>', 'implies': '>>', 'is equivalent to': '<->', 'not': '~'}
    item = ' '.join(args)
    return items_dict[item]


def formula(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def clause_body(there_is_clause):
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
    from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


