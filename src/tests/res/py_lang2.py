

def arithmetic(number, number_2):
   raise NotImplementedError


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


