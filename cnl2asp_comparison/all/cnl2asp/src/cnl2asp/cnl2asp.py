from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import tempfile
import traceback
from enum import Enum
from textwrap import indent
from typing import TextIO

from cnl2asp.utility.utility import Utility
from lark import Lark, UnexpectedCharacters
from lark.exceptions import VisitError

from cnl2asp.ASP_elements.asp_program import ASPProgram
from cnl2asp.exception.cnl2asp_exceptions import ParserError
from cnl2asp.specification.attribute_component import AttributeComponent
from cnl2asp.specification.entity_component import EntityComponent
from cnl2asp.converter.asp_converter import ASPConverter
from cnl2asp.parser.parser import CNLTransformer
from cnl2asp.specification.signaturemanager import SignatureManager
from cnl2asp.specification.specification import SpecificationComponent


class Cnl2asp:
    def __init__(self, cnl_input: TextIO | str, debug: bool = False):
        self._debug = debug
        if isinstance(cnl_input, str):
            self.cnl_input = cnl_input
            if os.path.isfile(cnl_input):
                self.cnl_input = open(cnl_input).read()
        else:
            self.cnl_input = cnl_input.read()

    def parse_input(self):
        with open(os.path.join(os.path.dirname(__file__), "grammar.lark"), "r") as grammar:
            cnl_parser = Lark(grammar.read(), propagate_positions=True)
            specification: SpecificationComponent = CNLTransformer().transform(cnl_parser.parse(self.cnl_input))
            return specification

    def compile(self, auto_link_entities: bool = True) -> str:
        SignatureManager.signatures = []
        Utility.AUTO_ENTITY_LINK = auto_link_entities
        specification: SpecificationComponent = self.parse_input()
        asp_converter: ASPConverter = ASPConverter()
        program: ASPProgram = specification.convert(asp_converter)
        return str(program)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file', type=str, nargs='?', default='')
    args = parser.parse_args()

    input_file = args.input_file

    in_file = open(input_file, 'r')
    cnl2asp = Cnl2asp(in_file, False)
    try:
        asp_encoding = cnl2asp.compile()
    except UnexpectedCharacters as e:
        in_file.seek(0)
        cnl_input = in_file.read()
        print(ParserError(e.char, e.line, e.column, e.get_context(cnl_input), cnl_input.splitlines()[e.line - 1],
                          list(e.allowed)))
        return ''
    except VisitError as e:
        print(e.args[0])
        return ''
    except Exception as e:
        print("Error in asp conversion:", str(e))
        return ''
    out = sys.stdout
    if args.output_file:
        if str(asp_encoding):
            print("Compilation completed.")
        out = open(args.output_file, "w")
    out.write(asp_encoding)