import string
import random

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler, create_var
from CNLWizard.libs.asp import Atom, Fact, Choice, Aggregate, Constraint, Comparison, WeakConstraint, Assignment


labels = dict()

def start(*propositions):
    res = ''
    for r in propositions:
        res += str(r) + '\n'
    return res


def compounded_range_clause(string_1, string_2, string_3):
    CnlWizardCompiler.signatures[string_1] = string_1, ['id'], ['id'], [None, None, None]
    res = []
    for v in range(int(string_2), int(string_3)+1):
        atom = CnlWizardCompiler.signatures[string_1]
        atom.fields['id'] = v
        res.append(atom)
    return '. '.join(map(str, res)) + '.'


def compound_match_clause(*string):
    CnlWizardCompiler.signatures[string[0]] = string[0], ['id'], ['id'], [None, None, None]
    res = []
    for v in string[1:]:
        atom = CnlWizardCompiler.signatures[string[0]]
        atom.fields['id'] = f'"{v}"'
        res.append(atom)
    return '. '.join(map(str, res)) + '.'


def is_initialized(atom):
    for field in atom.fields.values():
        if field != '_':
            return True
    return False


def initialize_entity(entity):
    if not is_initialized(entity):
        for field in entity.fields.keys():
            entity.fields[field] = create_var()

def quantified_choice(entity_1, verb, cardinality, entity_2):
    initialize_entity(entity_1)
    initialize_entity(entity_2)
    verb = simple_clause(entity_1, verb, entity_2)
    return Choice(verb, [entity_1], [entity_2], cardinality[0], cardinality[1])


def constraint(constraint_body):
    return Constraint(constraint_body)


def simple_clause(entity_1, verb, entity_2):
    if not verb.fields:
        fields = []
        for field in entity_1.fields:
            fields.append(entity_1.name + field)
        for field in entity_2.fields:
            fields.append(entity_2.name + field)
        CnlWizardCompiler.signatures[verb.name] = verb.name, fields, fields, [None, None, None]
    verb = Atom(verb)
    for key, value in entity_1.fields.items():
        verb.fields[entity_1.name + key] = str(value)
    for key, value in entity_2.fields.items():
        if entity_2.name + key in verb.fields and verb.fields[entity_2.name + key] != '_':
            verb.fields[entity_2.name + key] += ',' + str(value)
        else:
            verb.fields[entity_2.name + key] = str(value)
    return verb

def propositions(proposition):
    if isinstance(proposition, Atom):
        proposition = Fact(proposition)
    return proposition


def cardinality(*args):
    value = ' '.join(args)
    if value == 'exactly 1':
        return '1', '1'
    elif value == 'at least 1':
        return '1', ''
    else:
        return '', '1'


def constraint_body(when_then_clause):
    return str(when_then_clause)


def constraint_body_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def when_then_clause(simple_clause_1, simple_clause_2):
    return ', '.join([str(simple_clause_1), str(simple_clause_2)])


def negation(*args):
    return True


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def entity(string, label, attribute):
    string = string.lower()
    entity = CnlWizardCompiler.signatures[string]
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    if label and not attribute:
        entity.fields['id'] = label
    if label in labels:
        return labels[label]
    elif label:
        labels[label] = entity
    return entity


def verb(negation, string_1, attribute, string_2):
    sig_name = string_1.lower() + string_2.lower()
    if not sig_name in CnlWizardCompiler.signatures.signatures:
        CnlWizardCompiler.signatures[sig_name] = sig_name, [], [], [None, None, None]
    entity = CnlWizardCompiler.signatures[sig_name]
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def label(number):
    if number.isnumeric():
        return int(number)
    return number


