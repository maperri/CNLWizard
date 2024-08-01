from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


CnlWizardCompiler.config['signatures'] = False


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

def test_operation_operator(*args):
    items_dict = {'sum': 'sum(operand_1, operand_2)'}
    item = ' '.join(args)
    return items_dict[item]


def test_operation(*args):
    operator_index = None
    raise NotImplementedError('replace operator_index value')
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def operation(test_operation):
   raise NotImplementedError


def operand(number):
   raise NotImplementedError


def sum(operand_1, operand_2):
        raise NotImplementedError

