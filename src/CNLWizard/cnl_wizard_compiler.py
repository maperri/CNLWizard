import copy
import logging
import os
import sys
from typing import Callable

import lark

from lark import Lark, UnexpectedInput, Transformer

from CNLWizard.process_cnl import process_cnl_specification
from CNLWizard.reader import pyReader


class Signature:
    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields
        self.keys: list[str] = []
        self.type = ''
        self.lb = 0
        self.ub = 0

    def __str__(self):
        return f'{self.name}({",".join(map(str, self.fields.values()))})'


class Signatures:
    def __init__(self, signature_type: type = Signature, signature_field_null_value: any = '_'):
        self.signatures = dict()
        self.signature_type = signature_type
        self.signature_field_null_value = signature_field_null_value

    def __getitem__(self, item) -> Signature:
        return copy.deepcopy(self.signatures[item])

    def __setitem__(self, key: str, value: (str, list, list, (str, int, int))):
        """
        An item is a tuple containing the name,
        the list of fields, the list of keys (i.e. a subset of fields), and a type possibly with ranges.
        The user can set his custom signature_type and this method can
        instantiate the custom signature_type.
        Note that the user-defined signature_type must be compliant to the Signature interface.
        """
        fields_dictionary = dict()
        for field in value[1]:
            fields_dictionary.update({field: self.signature_field_null_value})
        self.signatures[key] = self.signature_type(value[0], fields_dictionary)
        self.signatures[key].keys = value[2]
        self.signatures[key].type = value[3][0] if value[3] else None
        if value[3]:
            if value[3][1]:
                self.signatures[key].lb = int(value[3][1])
            else:
                self.signatures[key].lb = None
            if value[3][2]:
                self.signatures[key].ub = int(value[3][2])
            else:
                self.signatures[key].ub = None


class CNLTransformer(Transformer):
    """
    Compiling the CNL specification.
    The default function call the corresponding defined function.
    """

    def __init__(self, functions: dict):
        super().__init__()
        self._functions = functions

    def __default__(self, data, children, meta):
        if data in self._functions:
            if not children:
                return lark.Discard
            call_res = self._functions[data](*children)
            if call_res is None:
                return lark.Discard
            return call_res
        return children

    def __default_token__(self, token):
        return token.value


class CnlWizardCompiler:
    signatures = Signatures()
    config = {
        'signatures': True,
        'var_substitution': True
    }

    def __init__(self):
        self.vars = dict()
        self.lists = dict()
        logging.basicConfig(format='%(levelname)s :: %(name)s :: %(message)s')
        self.logger = logging.getLogger(type(self).__name__)

    def compile(self, grammar_file: str, py_file: str, cnl_text_file: str):
        with open(grammar_file, 'r') as grammar:
            grammar = grammar.read()
        with open(cnl_text_file, 'r') as cnl_text_file:
            cnl_text_file = cnl_text_file.read()
        functions = pyReader().get_functions(py_file)
        lark = Lark(grammar)
        processed_cnl = process_cnl_specification(self, cnl_text_file, self.config)
        try:
            parse_tree = lark.parse(processed_cnl)
        except UnexpectedInput as e:
            self.logger.error(e)
            return ''
        return CNLTransformer(functions).transform(parse_tree)
