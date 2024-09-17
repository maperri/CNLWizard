import os

import yaml

from CNLWizard.reader import YAMLReader
from CNLWizard.writer import LarkGrammarWriter, PythonFunctionWriter


class CnlWizardGenerator:
    def __init__(self, yaml_file: str, import_dir: str, out_dir: str):
        self._specification = yaml_file
        if import_dir is None:
            import_dir = ''
        self._imported_libs = self._get_imported_grammars(import_dir)
        self._out_dir = out_dir

    def _import_internal_lib(self):
        return YAMLReader().read_specification(os.path.join(os.path.join(os.path.dirname(__file__), 'cnl_wizard_propositions.yaml')))

    def _is_specification_file(self, file: str) -> bool:
        if os.path.splitext(file)[1] == '.yaml':
            return True
        return False

    def _get_filename(self, file: str) -> str:
        return os.path.splitext(file)[0]

    def _get_imported_grammars(self, import_dir: str) -> dict:
        res = {'cnl_wizard': self._import_internal_lib()}
        if import_dir:
            for file in os.listdir(import_dir):
                if self._is_specification_file(file):
                    res[self._get_filename(file)] = YAMLReader().read_specification(os.path.join(import_dir, file))
        return res

    def generate(self):
        cnl = YAMLReader(self._imported_libs).read_specification(self._specification)
        grammar_writer = LarkGrammarWriter()
        for lang in cnl.get_languages():
            with open(os.path.join(self._out_dir, f'grammar_{lang}.lark'), 'w') as out:
                out.write(cnl.print(lang, grammar_writer))
            py_file = os.path.join(self._out_dir, f'py_{lang}.py')
            py_writer = PythonFunctionWriter()
            if os.path.exists(py_file):
                py_writer.import_fn(py_file)
            py_writer.write(cnl.print(lang, py_writer), py_file)

                    