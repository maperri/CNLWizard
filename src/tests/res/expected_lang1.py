from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(arithmetic):
    raise NotImplementedError


CnlWizardCompiler.config['signatures'] = False


def arithmetic(*args):
    raise NotImplementedError


def constraint(arithmetic):
    raise NotImplementedError


def entity(string, attribute):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def there_is_clause(entity):
    return Fact(entity)


def test_rule(arg):
    return True


def test_rule_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res
