from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*proposition):
    raise NotImplementedError


def proposition(disjunction):
    raise NotImplementedError


def simple_proposition(entity_1, entity_2):
    raise NotImplementedError


def negated_simple_proposition(entity_1, entity_2):
    raise NotImplementedError


def simple_clause(simple_proposition):
    raise NotImplementedError


def disjunction(simple_clause_1, simple_clause_2):
    raise NotImplementedError


def consequential(simple_clause_1, simple_clause_2):
    raise NotImplementedError


def entity(string, attribute):
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def there_is_clause(entity):
    return Fact(entity)


