from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


class Atom:
    def __init__(self, entity):
        self.name: str = entity.name
        self.fields: dict = entity.fields
        self.negation: str = ''

    def __str__(self):
        return f'{self.negation}{self.name}({",".join(self.fields.values())})'


class Fact:
    def __init__(self, head):
        self.head: Atom = head

    def __str__(self):
        return f'{self.head}.'


class Constraint:
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return f':- {", ".join(map(str, self.body))}.'


class Assignment:
    def __init__(self, head, body):
        self.head: list = head
        self.body: list = body

    def __str__(self):
        return f'{" | ".join(map(str, self.head))} :- {", ".join(map(str, self.body))}.'


def start(*proposition):
    res = ''
    for p in proposition:
        res += str(p) + '\n'
    return res


def start_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def simple_proposition(entity_1, entity_2):
    return (entity_1, entity_2)


def negated_simple_proposition(entity_1, entity_2):
    entity_2.negation = 'not '
    return (entity_1, entity_2)


def entity(string, attribute):
    try:
        entity = Atom(CnlWizardCompiler.signatures[string])
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def proposition(disjunction):
    return disjunction


def simple_clause(simple_proposition):
    field = simple_proposition[0].name + '_' + str(list(simple_proposition[0].fields.keys())[0])
    simple_proposition[1].fields[field] = list(simple_proposition[0].fields.values())[0]
    return simple_proposition


def disjunction(simple_1, simple_2):
    return Assignment([simple_1[1], simple_2[1]], [simple_1[0]])


def consequential(simple_1, simple_2):
    if not simple_1[1].negation:
        simple_1[1].negation = 'not '
    else:
        simple_1[1].negation = ''
    constraint = Constraint([simple_1[1], simple_2[1]])
    return constraint


def there_is_clause(entity):
    return Fact(entity)


