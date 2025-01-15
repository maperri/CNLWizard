from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*propositions):
    raise NotImplementedError


def compounded_range_clause(string_1, string_2, string_3):
    raise NotImplementedError


def compound_match_clause(*string):
    raise NotImplementedError


def quantified_choice(entity_1, verb, cardinality, entity_2):
    raise NotImplementedError


def constraint(constraint_body):
    raise NotImplementedError


def simple_clause(entity_1, verb, entity_2):
    raise NotImplementedError


def propositions(compounded_range_clause):
    raise NotImplementedError


def cardinality(*args):
    raise NotImplementedError


def constraint_body(when_then_clause):
    raise NotImplementedError


def constraint_body_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def when_then_clause(simple_clause_1, simple_clause_2):
    raise NotImplementedError


def negation(*args):
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


def label(number):
    raise NotImplementedError


def entity(string, label, attribute):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def verb(negation, string_1, attribute, string_2):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


