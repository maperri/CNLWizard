from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def constraint(arithmetic):
    raise NotImplementedError


def start(arithmetic):
    raise NotImplementedError


def entity(name, attributes):
    try:
        entity = CnlWizardCompiler.signatures[name]
        for name, value in attributes:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def there_is_clause(entity):
    raise NotImplementedError

