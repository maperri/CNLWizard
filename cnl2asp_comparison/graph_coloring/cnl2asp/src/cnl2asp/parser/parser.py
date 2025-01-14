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
from cnl2asp.parser.proposition_builder import PropositionBuilder
from cnl2asp.specification.attribute_component import AttributeComponent, ValueComponent, RangeValueComponent, \
    AttributeOrigin, AngleValueComponent
from cnl2asp.specification.component import Component
from cnl2asp.specification.entity_component import EntityComponent, EntityType
from cnl2asp.specification.problem import Problem
from cnl2asp.specification.proposition import Proposition, NewKnowledgeComponent, ConditionComponent, \
    CardinalityComponent, PREFERENCE_PROPOSITION_TYPE, PROPOSITION_TYPE
from cnl2asp.specification.relation_component import RelationComponent
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

    def implicit_definition_proposition(self, elem) -> None:
        for command in self._delayed_operations:
            command.execute()
        if elem[0]:
            SignatureManager.add_signature(elem[0])
        self._proposition.add_defined_attributes(self._defined_variables)
        self._problem.add_propositions(self._proposition.get_propositions())
        self._clear()

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
    def compounded_match_clause(self, meta, elem) -> EntityComponent:
        name: str = elem[0].lower()
        tail_attributes: list[(str, ValueComponent)] = elem[2] if elem[2] else []
        defined_entities: list[EntityComponent] = []
        for value in elem[1]:
            defined_entities.append(EntityComponent(name, '', [], [AttributeComponent(Utility.DEFAULT_ATTRIBUTE,
                                                                                      value, AttributeOrigin(name))]))
        for name, values in tail_attributes:
            if len(values) != len(defined_entities):
                raise CompilationError("Compounded tail has size different from values declared", meta.line)
            for i in range(len(values)):
                attribute = AttributeComponent(name, values[i])
                defined_entities[i].attributes.append(attribute)
        for entity in defined_entities[1:]:
            new_proposition = self._proposition.copy_proposition()
            new_proposition.new_knowledge.append(NewKnowledgeComponent(entity))
        self._proposition._original_rule.new_knowledge.append(NewKnowledgeComponent(defined_entities[0]))
        return defined_entities[0]


    def enumerative_definition_clause(self, elem):
        subject = elem[0]
        try:
            signature = SignatureManager.clone_signature(subject.get_name())
        except:
            signature = self._proposition.create_new_signature(subject)
            SignatureManager.add_signature(signature)
        copy: EntityComponent = signature.copy()
        copy.set_attributes_value(subject.keys + subject.attributes)
        subject.keys = copy.keys
        subject.attributes = copy.attributes
        verb: EntityComponent = elem[1]
        if subject.label or subject.attributes:
            self._proposition.add_requisite(subject)
            SignatureManager.add_signature(
                elem[0])  # we can have new definitions in subject position for this proposition
        else:
            # subject is an attribute value of the verb
            verb.attributes.append(
                AttributeComponent('id', ValueComponent(subject.get_name()), AttributeOrigin(verb.get_name())))
        object_list = elem[2] if elem[2] else []
        for idx, object_entity in enumerate(object_list):
            # replace the object elements with the proper signature if same of the subject
            for entity in object_entity.get_entities():
                if entity.get_name() == subject.get_name():
                    entity_signature = SignatureManager.clone_signature(entity.get_name())
                    entity_signature.label = entity.label
                    entity_signature.set_attributes_value(entity.get_keys_and_attributes())
                    object_list[idx] = entity_signature
        self._proposition.add_new_knowledge(NewKnowledgeComponent(verb,
                                                                  ConditionComponent([]), subject, verb.auxiliary_verb,
                                                                  object_list))
        self._proposition.add_requisite_list(object_list)
        for proposition in self._proposition.get_propositions():
            if subject.label or subject.attributes:
                object_list.insert(0, subject)
            self._make_new_knowledge_relations(proposition, object_list)

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

    def when_then_clause(self, elem):
        return elem[1]

    def terminal_clauses(self, elem):
        return [e for e in elem if e]

    def variable_substitution(self, elem):
        self._delayed_operations.append(SubstituteVariable(self._proposition, elem[0], elem[2]))


    def string_list(self, elem):
        return [ValueComponent(string) for string in elem]

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


    def _is_label(self, string: str) -> bool:
        if isinstance(string, EntityComponent):
            return False
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

    def NUMBER(self, elem) -> ValueComponent:
        return ValueComponent(elem.value)

    def string(self, elem) -> ValueComponent:
        if self._is_label(elem[0]):
            return ValueComponent(elem[0])
        return ValueComponent(elem[0])

    def ASSIGNMENT_VERB(self, verb):
        return verb

    def VERB_NEGATION(self, negation) -> bool:
        return True

    def QUANTITY_OPERATOR(self, quantity):
        if quantity == 'exactly':
            return QUANTITY_OPERATOR.EXACTLY
        elif quantity == 'at most':
            return QUANTITY_OPERATOR.AT_MOST
        elif quantity == 'at least':
            return QUANTITY_OPERATOR.AT_LEAST

    def VARIABLE(self, elem):
        return ValueComponent(elem.value)

    def COPULA(self, elem):
        return elem

    def NUMBER(self, elem):
        return elem.value

    def END_OF_LINE(self, end_of_line) -> None:
        return lark.Discard

    def cnl_is_one_of(self, elem) -> None:
        return lark.Discard

    def cnl_goes_from(self, elem) -> None:
        return lark.Discard


    def cnl_it_is_required_that(self, elem) -> PROPOSITION_TYPE:
        return PROPOSITION_TYPE.REQUIREMENT


