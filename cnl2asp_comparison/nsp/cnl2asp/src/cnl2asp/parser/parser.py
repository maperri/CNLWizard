from __future__ import annotations
import re
import string

from enum import Enum

import lark
from lark import Transformer, v_args

from cnl2asp.exception.cnl2asp_exceptions import LabelNotFound, ParserError, AttributeNotFound, EntityNotFound, \
    EntityNotFound, CompilationError, DuplicatedTypedEntity, AttributeGenericError
from cnl2asp.parser.command import SubstituteVariable, Command, DurationClause, CreateSignature, \
    RespectivelySubstituteVariable
from cnl2asp.parser.proposition_builder import PropositionBuilder, PreferencePropositionBuilder
from cnl2asp.specification.attribute_component import AttributeComponent, ValueComponent, RangeValueComponent, \
    AttributeOrigin, AngleValueComponent
from cnl2asp.specification.component import Component
from cnl2asp.specification.constant_component import ConstantComponent
from cnl2asp.specification.entity_component import EntityComponent, EntityType
from cnl2asp.specification.problem import Problem
from cnl2asp.specification.proposition import Proposition, NewKnowledgeComponent, ConditionComponent, \
    CardinalityComponent, PREFERENCE_PROPOSITION_TYPE, PROPOSITION_TYPE
from cnl2asp.specification.relation_component import RelationComponent
from cnl2asp.specification.aggregate_component import AggregateComponent, AggregateOperation
from cnl2asp.specification.operation_component import Operators, OperationComponent
from cnl2asp.specification.signaturemanager import SignatureManager
from cnl2asp.specification.specification import SpecificationComponent
from cnl2asp.utility.utility import Utility
from cnl2asp.exception.cnl2asp_exceptions import TypeNotFound


class QUANTITY_OPERATOR(Enum):
    EXACTLY = 0
    AT_MOST = 1
    AT_LEAST = 2


PRONOUNS = ['i', 'you', 'he', 'she', 'it', 'we', 'you', 'they']  # they are skipped if subject
DUMMY_ENTITY = EntityComponent('', '', [], [])


def is_verb_to_have(word: str):
    return word in ["have ", "have a ", "have an ", "has ", "has a ", "has an "]


class CNLTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._specification: SpecificationComponent = SpecificationComponent()
        self._problem: Problem = Problem()
        self._proposition: PropositionBuilder = PropositionBuilder()
        self._delayed_operations: list[Command] = []
        self._defined_variables: list[str] = []

    def _new_field_value(self, name: str = '') -> ValueComponent:
        if name:
            result = re.sub(r'[AEIOU]', '', name, flags=re.IGNORECASE).upper()
            if result in self._defined_variables:
                match = re.findall(r'\d+', name)
                if match:
                    last_num = int(match[-1])
                    name = name.rstrip(string.digits)
                    last_num += 1
                else:
                    last_num = 1
                return self._new_field_value(f'{name}{last_num}')
            self._defined_variables.append(result)
            return ValueComponent(result)

    def start(self, elem) -> SpecificationComponent:
        self._specification.add_problem(self._problem)
        return self._specification

    def specification(self, elem):
        self._specification.add_problem(self._problem)
        self._problem = Problem()


    def _clear(self):
        self._proposition = PropositionBuilder()
        self._delayed_operations = []
        self._defined_variables = []

    def explicit_definition_proposition(self, elem):
        if elem[0]:
            SignatureManager.add_signature(elem[0])
        self._clear()

    def standard_definition(self, elem) -> EntityComponent:
        entity_keys = []
        name = elem[0].lower()
        if elem[1]:
            for key in elem[1]:
                if not key.origin:
                    key.origin = AttributeOrigin(name)
                entity_keys.append(key)
        entity_attributes = []
        if elem[2]:
            for attributes in elem[2:]:
                for attribute in attributes:
                    if not attribute.origin:
                        attribute.origin = AttributeOrigin(name)
                    entity_attributes.append(attribute)
        return EntityComponent(name, '', entity_keys, entity_attributes)

    def keys_list(self, list_parameters) -> list[AttributeComponent]:
        res = []
        # Discard prepositions
        for elem in list_parameters:
            for attribute in elem:
                res.append(attribute)
        return res

    def parameter_definition(self, parameter) -> list[AttributeComponent]:
        name = parameter[:]
        origin = self._parse_parameter_origin(name)
        if origin and not name:
            keys = SignatureManager.clone_signature(parameter[-1]).get_keys()
            res = []
            for key in keys:
                key_origin = AttributeOrigin(origin.name, key.origin)
                res.append(AttributeComponent(key.get_name(), ValueComponent(Utility.NULL_VALUE), key_origin))
            return res
        else:
            name = '_'.join(name)
        return [AttributeComponent(name.strip(), ValueComponent(Utility.NULL_VALUE), origin)]

    def implicit_definition_proposition(self, elem) -> None:
        for command in self._delayed_operations:
            command.execute()
        if elem[0]:
            SignatureManager.add_signature(elem[0])
        self._proposition.add_defined_attributes(self._defined_variables)
        self._problem.add_propositions(self._proposition.get_propositions())
        self._clear()

    def constant_definition_clause(self, elem):
        value = ValueComponent(elem[1]) if elem[1] else ValueComponent('')
        self._specification.add_constant(ConstantComponent(elem[0], value))

    @v_args(meta=True)
    def compounded_range_clause(self, meta, elem) -> EntityComponent:
        name: str = elem[0].lower()
        value = RangeValueComponent(elem[1], elem[2])
        try:
            entity = SignatureManager.clone_signature(name)
            entity_keys = entity.get_keys()
            if len(entity.get_keys()) > 1:
                raise CompilationError(
                    f"Impossible to use compound range clause for an entity (\"{name}\" with multiple keys", meta.line)
            entity.set_attribute_value(entity_keys[0].get_name(), value, entity_keys[0].origin)
        except:
            entity = EntityComponent(name, '', [],
                                     [AttributeComponent(Utility.DEFAULT_ATTRIBUTE, value, AttributeOrigin(name))])
        self._proposition.add_new_knowledge(NewKnowledgeComponent(entity))
        return entity



    @v_args(meta=True)
    def standard_proposition(self, meta, elem):
        try:
            for command in self._delayed_operations:
                command.execute()
            self._proposition.add_defined_attributes(self._defined_variables)
            self._problem.add_propositions(self._proposition.get_propositions())
            self._clear()
        except Exception as e:
            raise CompilationError(str(e), meta.line)

    def _make_new_knowledge_relations(self, proposition: Proposition, components: list[Component] = None):
        if Utility.AUTO_ENTITY_LINK:
            if components:
                for component in components:
                    for entity in component.get_entities_to_link_with_new_knowledge():
                        for new_knowledge in proposition.new_knowledge:
                            proposition.relations.append(RelationComponent(new_knowledge.new_entity, entity))
            for new_knowledge in proposition.new_knowledge:
                for condition_entity in new_knowledge.condition.components:
                    for entity in condition_entity.get_entities_to_link_with_new_knowledge():
                        proposition.relations.append(
                            RelationComponent(new_knowledge.new_entity, entity))


    def whenever_clause(self, elem):
        if elem[0]:
            elem[1].negated = True
        self._proposition.add_requisite(elem[1])


    def _handle_new_definition_proposition(self, subject: EntityComponent, cardinality: CardinalityComponent):
        self._proposition.add_cardinality(cardinality)
        self._proposition.add_subject(subject.copy())
        if subject is not DUMMY_ENTITY:
            for proposition in self._proposition.get_propositions():
                for new in proposition.new_knowledge:
                    # normally only keys are linked to an head.
                    # Here we are forcing to link also subject initialized attributes.
                    new.new_entity.attributes += [
                        AttributeComponent(attribute.get_name(), ValueComponent(Utility.NULL_VALUE),
                                           AttributeOrigin(new.new_entity.get_name(), attribute.origin))
                        for attribute in subject.get_initialized_attributes()]
                self._make_new_knowledge_relations(proposition, [subject])

    def quantified_choice_proposition(self, elem):
        cardinality = self._proposition.get_cardinality()
        if elem[2] == 'can' and not self._proposition.get_cardinality():
            cardinality = CardinalityComponent(None, None)
        self._handle_new_definition_proposition(elem[1], cardinality)
        self._proposition.add_requisite(elem[1])
        return elem[1]

    def foreach_clause(self, elem):
        objects: list[EntityComponent] = elem[0]
        self._proposition.add_requisite_list(objects)
        for proposition in self._proposition.get_propositions():
            for new_knowledge in proposition.new_knowledge:
                for entity in elem[0]:
                    proposition.relations.append(RelationComponent(new_knowledge.new_entity, entity))

    def constraint_proposition(self, elem):
        if elem[0] == PROPOSITION_TYPE.REQUIREMENT:
            if isinstance(elem[1], list):
                for e in elem[1]:
                    e.negate()
            else:
                elem[1].negate()

    def simple_clause_conjunction(self, elem):
        entities = []
        for entities_list in elem:
            for idx, entity in enumerate(entities_list):
                if idx == 1:
                    entities.append(entity)
                self._proposition.add_requisite(entity)
        return entities

    def simple_clause_wrv(self, elem) -> list[EntityComponent]:
        subject = elem[0]
        verb = elem[1]
        objects = elem[2] if elem[2] else []
        entities = [subject, verb, *objects]
        relations = [RelationComponent(subject, verb)]
        for object_elem in objects:
            relations.append(RelationComponent(verb, object_elem))
        self._proposition.add_relations(relations)
        return entities

    def terminal_clauses(self, elem):
        return [e for e in elem if e]

    def variable_substitution(self, elem):
        self._delayed_operations.append(SubstituteVariable(self._proposition, elem[0], elem[2]))

    def variable_respectively_substitution(self, elem):
        self._delayed_operations.append(RespectivelySubstituteVariable(self._proposition, elem[0], elem[2]))

    def string_list(self, elem):
        return [ValueComponent(string) for string in elem]

    def comparison_operand(self, elem):
        return elem[0]

    def arithmetic_operand(self, elem):
        operation = OperationComponent(elem[0], elem[2], *elem[3:])
        if elem[1]:
            return OperationComponent(Operators.ABSOLUTE_VALUE, operation)
        return operation

    def comparison(self, elem):
        comparison = OperationComponent(elem[1], elem[0], elem[2])
        if elem[3] and isinstance(elem[0], AggregateComponent):
            elem[0].body += elem[3]
        self._proposition.add_requisite(comparison)
        return comparison

    def between_comparison(self, elem):
        return self.comparison([elem[0], Operators.BETWEEN, [elem[1], elem[2]], None])


    def aggregate_active_clause(self, elem) -> AggregateComponent:
        discriminant = [elem[1], elem[2]] if elem[2] else [elem[1]]
        body = [elem[3]]
        if elem[4]:
            body += elem[4]
            for entity in elem[4]:
                self._proposition.add_relations([RelationComponent(entity, elem[3])])
        return AggregateComponent(elem[0], discriminant, body)

    @v_args(meta=True)
    def aggregate_passive_clause(self, meta, elem) -> AggregateComponent:
        discriminant = [elem[1], elem[3]] if elem[3] else [elem[1]]
        verb: EntityComponent = elem[5]
        if elem[2]:
            try:
                verb.set_attributes_value(elem[2])
            except AttributeNotFound as e:
                raise CompilationError(str(e), meta.line)
        body = [verb]
        AggregateComponent(elem[0], discriminant, body)
        subject = elem[4]
        self._proposition.add_requisite(subject)
        self._proposition.add_relations([RelationComponent(subject, verb)])
        if elem[6]:
            body += elem[6]
            for entity in elem[6]:
                self._proposition.add_relations([RelationComponent(entity, verb)])
        return AggregateComponent(elem[0], discriminant, body)

    def preference_with_aggregate_clause(self, elem):
        if elem[3]:
            new_var = self._new_field_value(elem[3].operation.name)
            self._proposition.add_requisite(OperationComponent(Operators.EQUALITY, elem[3], new_var))
            self._proposition.add_weight(new_var)

    @v_args(meta=True)
    def single_quantity_cardinality(self, meta, elem):
        cardinality = None
        if elem[0] == QUANTITY_OPERATOR.EXACTLY:
            cardinality = CardinalityComponent(elem[1], elem[1])
        elif elem[0] == QUANTITY_OPERATOR.AT_MOST:
            cardinality = CardinalityComponent(None, elem[1])
        elif elem[0] == QUANTITY_OPERATOR.AT_LEAST:
            cardinality = CardinalityComponent(elem[1], None)
        if self._proposition.get_cardinality() and self._proposition.get_cardinality() != cardinality:
            raise CompilationError('Error multiple cardinality provided in the same proposition', meta.line)
        else:
            self._proposition.add_cardinality(cardinality)


    def conjunctive_object_list(self, elem):
        return [x for x in elem]

    def predicate_with_objects(self, elem):
        verb: EntityComponent = elem[0]
        objects: list[Component] = elem[2]
        new_knowledge = NewKnowledgeComponent(verb, ConditionComponent(objects), None, verb.auxiliary_verb, objects)
        new_knowledge.objects = objects
        if elem[-1]:
            self._delayed_operations.append(DurationClause(self._proposition, new_knowledge, elem[-2], elem[-1]))
        self._proposition.add_new_knowledge(new_knowledge)

    def parameter_list(self, list_parameters) -> list[AttributeComponent]:
        res = []
        # Discard prepositions
        for elem in list_parameters:
            if not isinstance(elem, lark.Token):
                res.append(elem)
        return list(res)

    def _parse_parameter_origin(self, name: list[str]):
        try:
            SignatureManager.clone_signature(name[0])
            return AttributeOrigin(name.pop(0), self._parse_parameter_origin(name))
        except:
            return None

    def _parse_entity_parameter(self, name, label):
        try:
            entity = self._proposition.get_entity_by_label(label)
            if entity.get_name() == name[0]:
                return entity
        except LabelNotFound:
            return None
        return None

    def _parse_parameter_value(self, parameter_name, explicit_value, operator, operand_value):
        result = Utility.NULL_VALUE
        if explicit_value:
            result = explicit_value
        elif operator == Operators.EQUALITY:
            result = operand_value
        elif operator:
            result = self._new_field_value(parameter_name)
        self._defined_variables.append(result)
        return ValueComponent(result)

    def _parse_parameter_operation(self, attribute, operator, operand):
        if operator and attribute.value != operand:
            operation = OperationComponent(operator, attribute.value, operand)
            if attribute.is_angle():
                operation.operands[0] = AngleValueComponent(attribute.value)
            attribute.operations = [operation]

    def parameter(self, parameter) -> EntityComponent | AttributeComponent:
        name = parameter[:-4]
        if self._parse_entity_parameter(name, parameter[-4]):
            return self._parse_entity_parameter(name, parameter[-4])
        origin = self._parse_parameter_origin(name)
        if origin and not name:
            name = SignatureManager.clone_signature(parameter[-5]).get_keys()[0].get_name()
        else:
            name = '_'.join(name)
        if not origin and SignatureManager.is_temporal_entity(name.strip()):
            origin = AttributeOrigin(name.strip())
        attribute = AttributeComponent(name.strip(),
                                       self._parse_parameter_value(name, parameter[-4], parameter[-3], parameter[-2]),
                                       origin)
        self._parse_parameter_operation(attribute, parameter[-3], parameter[-2])
        self._proposition.add_discriminant([attribute])
        return attribute

    def aggregate_parameter(self, parameter):
        name = parameter[:-1]
        origin = self._parse_parameter_origin(name)
        if origin and not name:
            name = SignatureManager.clone_signature(parameter[-2]).get_keys()[0].get_name()
        else:
            name = '_'.join(name)
        if not origin and SignatureManager.is_temporal_entity(name.strip()):
            origin = AttributeOrigin(name.strip())
        attribute = AttributeComponent(name.strip(),
                                       self._parse_parameter_value(name, parameter[-1], None, None),
                                       origin)
        self._proposition.add_discriminant([attribute])
        return attribute

    def expression(self, elem):
        return ''.join(elem)

    def _is_label(self, string: str) -> bool:
        if isinstance(string, EntityComponent):
            return False
        if string.isupper():
            return True
        return False

    def is_variable(string: str) -> bool:
        if string.isupper():
            return True
        return False

    def _is_pronouns(self, elem: str) -> bool:
        return elem in PRONOUNS

    @v_args(meta=True, inline=True)
    def simple_entity(self, meta, name, label, entity_temporal_order_constraint, define_subsequent_event,
                      parameter_list, new_definition=False) -> EntityComponent | str:
        if self._is_label(name):
            try:
                return self._proposition.get_entity_by_label(name)
            except LabelNotFound as e:
                raise CompilationError(str(e), meta.line)
        name = name.lower()
        parameter_list = parameter_list if parameter_list else []
        if self._is_pronouns(name):
            return DUMMY_ENTITY
        try:
            if label:
                entity = self._proposition.get_entity_by_label(label)
            else:
                raise LabelNotFound("")
        except (LabelNotFound, AttributeNotFound):
            try:
                entity = SignatureManager.clone_signature(name)
                entity.label = label
            except EntityNotFound as e:
                # this is the case that we are defining a new entity
                if new_definition:
                    entity = EntityComponent(name, label, [],
                                             [attribute for attribute in parameter_list if
                                              isinstance(attribute, AttributeComponent)])
                else:
                    raise CompilationError(str(e), meta.line)
        try:
            entity.set_attributes_value(parameter_list, self._proposition)
        except AttributeNotFound as e:
            raise CompilationError(str(e), meta.line)
        if entity.label_is_key_value():
            entity.set_label_as_key_value()
            self._defined_variables.append(ValueComponent(entity.label))
        if entity_temporal_order_constraint:
            self.temporal_constraint(meta, [entity] + entity_temporal_order_constraint)
        if define_subsequent_event:
            try:
                self.__substitute_subsequent_event(entity, define_subsequent_event[0], define_subsequent_event[1])
            except TypeNotFound as e:
                raise CompilationError(str(e), meta.line)
        return entity


    @v_args(meta=True)
    def verb(self, meta, elem):
        elem[4] = elem[4][0:-1] if elem[4][-1] == 's' else elem[4]  # remove 3rd person final 's'
        verb_name = '_'.join([elem[4], elem[8]]) if elem[8] else elem[4]
        verb_name = verb_name.lower()
        if is_verb_to_have(elem[0]):
            verb_name = verb_name.removesuffix('_to')
        entity: EntityComponent = self.simple_entity(meta, verb_name, '', elem[5], elem[6], elem[7],
                                                     new_definition=True)
        if elem[3]:
            entity = self.entity([elem[3], entity])
        if elem[2]:
            entity.negated = True
        if elem[1]:
            self._proposition.add_cardinality(elem[1])
        self._delayed_operations.append(CreateSignature(self._proposition, entity))
        entity.auxiliary_verb = elem[0]
        return entity

    def cnl_it_is_preferred(self, elem):
        self._proposition = PreferencePropositionBuilder()

    def optimization_statement(self, elem):
        if elem == PREFERENCE_PROPOSITION_TYPE.MAXIMIZATION:
            self._proposition.add_type(PREFERENCE_PROPOSITION_TYPE.MAXIMIZATION)
        elif elem == PREFERENCE_PROPOSITION_TYPE.MINIMIZATION:
            self._proposition.add_type(PREFERENCE_PROPOSITION_TYPE.MINIMIZATION)

    def optimization_operator(self, elem):
        if elem[0] == PREFERENCE_PROPOSITION_TYPE.MAXIMIZATION:
            self._proposition.add_type(PREFERENCE_PROPOSITION_TYPE.MAXIMIZATION)
        elif elem[0] == PREFERENCE_PROPOSITION_TYPE.MINIMIZATION:
            self._proposition.add_type(PREFERENCE_PROPOSITION_TYPE.MINIMIZATION)

    def CNL_MINIMIZED(self, elem):
        return PREFERENCE_PROPOSITION_TYPE.MINIMIZATION


    def PRIORITY_LEVEL(self, elem):
        if elem.value == 'low':
            self._proposition.add_level(1)
        elif elem.value == 'medium':
            self._proposition.add_level(2)
        elif elem.value == 'high':
            self._proposition.add_level(3)

    def NUMBER(self, elem) -> ValueComponent:
        return ValueComponent(elem.value)

    def string(self, elem) -> ValueComponent:
        if self._is_label(elem[0]):
            return ValueComponent(elem[0])
        return ValueComponent(elem[0])

    def ASSIGNMENT_VERB(self, verb):
        return verb


    def QUANTITY_OPERATOR(self, quantity):
        if quantity == 'exactly':
            return QUANTITY_OPERATOR.EXACTLY
        elif quantity == 'at most':
            return QUANTITY_OPERATOR.AT_MOST
        elif quantity == 'at least':
            return QUANTITY_OPERATOR.AT_LEAST

    def COMPARISON_OPERATOR(self, elem):
        operator = elem.value
        if operator == "the same as" or operator == "equal to":
            return Operators.EQUALITY
        if operator == "different from":
            return Operators.INEQUALITY
        if operator == "more than" or operator == "greater than":
            return Operators.GREATER_THAN
        if operator == "less than":
            return Operators.LESS_THAN
        if operator == "greater than or equal to" or operator == "at least":
            return Operators.GREATER_THAN_OR_EQUAL_TO
        if operator == "less than or equal to" or operator == "at most":
            return Operators.LESS_THAN_OR_EQUAL_TO
        if operator == "not after":
            return Operators.LESS_THAN_OR_EQUAL_TO
        if operator == "between":
            return Operators.BETWEEN

    def ARITHMETIC_OPERATOR(self, elem):
        operator = elem.value
        if operator == "the sum":
            return Operators.SUM
        if operator == "the difference":
            return Operators.DIFFERENCE
        if operator == "the product":
            return Operators.MULTIPLICATION
        if operator == "the division":
            return Operators.DIVISION

    def PARAMETER_NAME(self, elem):
        parameter = elem.value
        return parameter if parameter else elem.value


    def AGGREGATE_OPERATOR(self, elem):
        operator = elem.value
        if operator == "the number":
            return AggregateOperation.COUNT
        if operator == "the total":
            return AggregateOperation.SUM
        if operator == "the highest" or operator == "the biggest":
            return AggregateOperation.MAX
        if operator == "the lowest" or operator == "the smallest":
            return AggregateOperation.MIN

    def VARIABLE(self, elem):
        return ValueComponent(elem.value)

    def COPULA(self, elem):
        return elem

    def NUMBER(self, elem):
        return elem.value

    def END_OF_LINE(self, end_of_line) -> None:
        return lark.Discard

    def cnl_whenever_there_is(self, elem) -> None:
        return lark.Discard

    def cnl_goes_from(self, elem) -> None:
        return lark.Discard


    def cnl_is_identified(self, elem) -> None:
        return lark.Discard

    def cnl_is_a_constant(self, elem) -> None:
        return lark.Discard

    def cnl_it_is_prohibited_that(self, elem) -> PROPOSITION_TYPE:
        return PROPOSITION_TYPE.CONSTRAINT

    def cnl_it_is_required_that(self, elem) -> PROPOSITION_TYPE:
        return PROPOSITION_TYPE.REQUIREMENT

    def cnl_as_much_as_possible(self, elem) -> None:
        return PREFERENCE_PROPOSITION_TYPE.MAXIMIZATION

