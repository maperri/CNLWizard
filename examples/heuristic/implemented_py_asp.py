from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from graphlib import TopologicalSorter


class Atom:
    def __init__(self, entity):
        self.name: str = entity.name
        self.fields: dict = entity.fields
        self.negation: str = ''

    def __str__(self):
        # modifica: se l'atomo non ha attributi, viene stampata la stringa vuota
        attributes = f'({",".join(self.fields.values())})' if self.fields else ''
        return f'{self.negation}{self.name}{attributes}'


class Fact:
    def __init__(self, head):
        self.head: Atom = head

    def __str__(self):
        return f'{self.head}.'


class Constant:
    def __init__(self, name, value):
        self.name: str = name
        self.value: str = value

    def __str__(self):
        return f'#const {self.name}={self.value}.'


class Constraint:
    def __init__(self, atoms):
        self.atoms = atoms

    def __str__(self):
        return f':- {", ".join(map(str, self.atoms))}.'


class Aggregate:
    def __init__(self, operator, discriminant, body):
        self.operator: str = operator
        self.discriminant: list = discriminant
        self.body: list = body

    def __str__(self):
        return f'#{self.operator}{{{", ".join(map(str, self.discriminant))}: {", ".join(map(str, self.body))}}}'


class Choice:
    def __init__(self, head, body, condition, lb='', ub=''):
        self.head: list = head
        self.body: list = body
        self.condition: list = condition
        self.lb: str = lb
        self.ub: str = ub

    def __str__(self):
        str_cond = ": " + ", ".join(map(str, self.condition)) if self.condition else ''
        # modifica: se la choice non ha body, viene stampata la stringa vuota
        str_body = " :- " + ", ".join(map(str, self.body)) if self.body else ''
        # modifica: ora si possono avere più atomi disgiuntivi nella head
        str_head = "; ".join(map(str, self.head)) if self.head else ''
        return f'{self.lb}{{{str_head}{str_cond}}}{self.ub}{str_body}.'


class Assignment:
    def __init__(self, head, body):
        self.head: list = head
        self.body: list = body

    def __str__(self):
        return f'{" | ".join(map(str, self.head))} :- {", ".join(map(str, self.body))}.'


class WeakConstraint:
    def __init__(self, body, weight, discriminant):
        self.body: list = body
        self.weight: int = weight
        self.discriminant: list = discriminant

    def __str__(self):
        return f':~ {", ".join(map(str, self.body))}. [{self.weight}@{", ".join(map(str, self.discriminant))}]'


class Heuristic:
    def __init__(self, head, body, heur_priority):
        self.head: Atom = head
        self.body: list = ": " + ", ".join(map(str, body)) if body else ''
        self.heur_priority = f'@{heur_priority}' if heur_priority else ''
    

class SignHeuristic(Heuristic):
    def __init__(self, head, body, sign, heur_priority):
        super().__init__(head, body, heur_priority)
        self.sign = '1' if sign else '-1'

    def __str__(self):
        return f'#heuristic {self.head}{self.body}. [{self.sign}{self.heur_priority},sign]'
    

class TrueFalseHeuristic(SignHeuristic):
    def __init__(self, head, body, heur_negation, heur_level, heur_priority):
        super().__init__(head, body, heur_negation, heur_priority)
        self.heur_level = heur_level if heur_level else ''

    def __str__(self):
        str_heur_negation = 'false' if self.heur_negation else 'true'
        return f'#heuristic {self.head}{self.body}. [{self.heur_level}{self.heur_priority},{str_heur_negation}]'
    

class LevelHeuristic(Heuristic):
    def __init__(self, head, body, heur_level, heur_priority):
        super().__init__(head, body, heur_priority)
        self.heur_level = heur_level

    def __str__(self):
        return f'#heuristic {self.head}{self.body}. [{self.heur_level}{self.heur_priority},level]'




def start(*rules):
    res = ''
    for r in rules:
        res += str(r) + '\n'
    res += str(DictPriorityGraph())
    return res


def propositions(p):
    return p


def there_is_clause(entity):
    return Fact(entity)


def constant(string, attribute_value):
    return Constant(string, attribute_value)


def constraint(constraint_body, whenever_clause):
    if not isinstance(constraint_body, list):
        constraint_body = [constraint_body]
    if not isinstance(whenever_clause, list):
        whenever_clause = [whenever_clause]
    return Constraint(constraint_body + whenever_clause) if whenever_clause else Constraint(constraint_body)


def whenever_then_clause_choice(whenever_clause, cardinality, then_subject, then_object):
    # modifica: trasforma in lista solo se esiste (non è None)
    if whenever_clause and not isinstance(whenever_clause, list):
        whenever_clause = [whenever_clause]
    # modifica: trasforma in lista solo se esiste (non è None)
    if then_subject and not isinstance(then_subject, list):
        then_subject = [then_subject]
    # modifica: trasforma in lista solo se esiste (non è None)
    if then_object and not isinstance(then_object, list):
        then_object = [then_object]
    whenever_then_clause_choice = Choice(then_subject, whenever_clause, then_object)
    if cardinality:
        whenever_then_clause_choice.lb = cardinality[0]
        whenever_then_clause_choice.ub = cardinality[1]
    return whenever_then_clause_choice


def whenever_then_clause_assignment(whenever_clause, then_subject):
    return Assignment([then_subject], whenever_clause)


def weak_constraint(level, comparison, whenever_clause):
    body = [comparison]
    if whenever_clause:
        if not isinstance(whenever_clause, list):
            whenever_clause = [whenever_clause]
        body += whenever_clause
    return WeakConstraint(body, level, [1])


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def comparison_operator(*args):
    items_dict = {'equal to': '==', 'different from': '!=', 'lower than': '<', 'greater than': '>',
                  'lower than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator.join(map(str, args))


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def entity(negation, _, name, attributes):
    entity = Atom(CnlWizardCompiler.signatures[name])
    # modifica: se non esistono gli attributi, non li inserisce nel campo fields
    if attributes:
        for name, value in attributes:
            entity.fields[name] = value
    if negation:
        entity.negation = 'not '
    return entity


def cardinality(*value):
    value = ' '.join(value)
    if value == 'exactly one':
        return '1', '1'
    elif value == 'at least one':
        return '1', ''
    else:
        return '', '1'


def level(*value):
    value = ' '.join(value)
    if value == 'low':
        return '1'
    elif value == 'medium':
        return '2'
    else:
        return '3'


def aggregate_operator(*value):
    value = ' '.join(value)
    if value == 'the number of':
        return 'count'
    elif value == 'the total of':
        return 'sum'
    elif value == 'the lowest value of':
        return 'min'
    else:
        return 'max'


def verb(name, attributes, string):
    verb = Atom(CnlWizardCompiler.signatures[name + string])
    for parameter in attributes:
        verb.fields[parameter[0]] = parameter[1]
    return verb


def aggregate(aggregate_operator, attribute_name, entity):
    parameter_value = entity.fields[attribute_name]
    return Aggregate(aggregate_operator, [parameter_value], [entity])


def negation(args):
    return True


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def then_object_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def whenever_clause_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def disjunction_then_subject_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def comparison_operand(arg):
    return arg


def math_operand(entity):
   return entity


def attribute_value(string):
   return string


def whenever_clause(entity):
   return entity


def disjunction_then_subject(then_subject):
   return then_subject


def constraint_body(entity):
   return entity


def constraint_body_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def then_subject(entity):
    return entity


def then_object(then_subject):
   return then_subject


def heuristic(clause):
    return clause


def true_sign(arg):
    return True


def false_sign(arg):
    return False


def sign(sign):
    return sign


#def sign(heur_negation):
#    return bool(heur_negation)


class DictPriorityGraph:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dict = dict()         
        return cls._instance
    

    def addNode(self, atom, if_clause, sign):
        if atom not in self._instance.dict:
            self._instance.dict[atom] = list()
        
        if if_clause:
            if_clause = set(str(x) for x in if_clause)
        else:
            if_clause = set()

        index = 0
        for rule in self._instance.dict[atom]:
            if if_clause.issubset(rule[0]):
                self._instance.dict[atom].insert(index, (if_clause, sign))
                return
            index += 1
                        
        self._instance.dict[atom].append((if_clause, sign))

        


    def __str__(self):
        res = ''
        for atom, list in self._instance.dict.items():
            priority_rate = 1
            '''
            print("1----------------------")
            for r in list:
                if not r[0]:
                    print('0', end='')
                else:
                    print(f'({", ".join(str(e) for e in r[0])})', end='  ')
                print()
            print("2----------------------")
            '''
            for rule in list:
                conditions = f': {", ".join(x for x in rule[0])}'if rule[0] else ''
                sign = '1' if rule[1] else '-1'
                priority = f'@{priority_rate}'
                r = f'#heuristic {atom}{conditions}. [{sign}{priority}, sign]'
                res += str(r) + '\n'
                priority_rate += 1
        return res



def sign_heuristic_clause(if_clause, then, preferred_that, entity, sign, heur_priority):
    if if_clause and not isinstance(if_clause, list):
        if_clause = [if_clause]
    dict = DictPriorityGraph()
    dict.addNode(str(entity), if_clause, sign)
    #return SignHeuristic(entity, if_clause, sign, heur_priority)


def true_false_heuristic_clause(if_clause, then, preferred_that, entity, sign, heur_level, heur_priority):
    if if_clause and not isinstance(if_clause, list):
        if_clause = [if_clause]
    return TrueFalseHeuristic(entity, if_clause, sign, heur_level, heur_priority)


def level_heuristic_clause(syntax_clause):
    return syntax_clause


def level_heuristic_clause_first_syntax(if_clause, then, preferred_that, entity, has, heur_level, heur_priority):
    if if_clause and not isinstance(if_clause, list):
        if_clause = [if_clause]
    return LevelHeuristic(entity, if_clause, heur_level, heur_priority)


def level_heuristic_clause_second_syntax(_):
    return None


def level_heuristic_clause_second_syntax_body(body):
    return body


def level_heuristic_clause_second_syntax_body_concat(*entity_concat):
    if entity_concat and not isinstance(entity_concat, list):
        entity_concat = list(entity_concat)
    entity_concat = [
        e for e in entity_concat
        if (
            isinstance(e, Atom) or
            (isinstance(e, list) and all(isinstance(el, Atom) for el in e))
        )
    ]
    g = Graph()
    while len(entity_concat) >= 2:
        second = entity_concat.pop()
        if not isinstance(second, list):
            second = [second]
        first = entity_concat[-1]
        if not isinstance(first, list):
            first = [first]
        for arg_first in first:
            for arg_second in second:
                g.addNode(arg_first, arg_second)
    


#def level_heuristic_clause_second_syntax_concat(*entity_concat):
#    if entity_concat and not isinstance(entity_concat, list):
#        entity_concat = list(entity_concat)
#    level_heuristics = []
#    level = 1
#    while len(entity_concat) > 0:
#        e = entity_concat.pop()
#        if isinstance(e, Atom):
#            level_heuristics.insert(0, LevelHeuristic(e, None, str(level), None))
#        elif isinstance(e, list):
#            for sameLev in e:
#                level_heuristics.insert(0, LevelHeuristic(sameLev, None, str(level), None))
#        level += 1
#    res = ''
#    for r in level_heuristics:
#        res += str(r) + '\n'
#    return res


def if_clause(if_there_is, entity):
   return entity


def if_clause_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def heur_negation(args):
    return True


def heur_level(with_level, value):
    return str(value)


def heur_priority(with_priority, value):
    return str(value)


class Graph:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.structure = TopologicalSorter()            
        return cls._instance
    

    def addNode(self, first, second):
        self.structure.add(str(first), str(second))


    def __str__(self):
        self._instance.structure.prepare()
        layers = []
        while self._instance.structure.is_active():
            ready = list(self._instance.structure.get_ready())
            layers.append(ready)
            for node in ready:
                self._instance.structure.done(node)
        res = ''
        level = 10
        for layer in layers:
            for atom in layer:
                r = f'#heuristic {atom}. [{level}, level]'
                res += str(r) + '\n'
            level += 10
        return res
    

def graph(arg):
    return Graph()


def entity_conjunction_concat(*args):
    args = [a for a in args if isinstance(a, Atom)]
    res = []
    for arg in args:
        res.append(arg)
    return res


def entity_conjunction(entity):
    return entity

