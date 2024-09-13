import os

from CNLWizard.reader import YAMLReader
from CNLWizard.writer import LarkGrammarWriter, PythonFunctionWriter


class CnlWizardGenerator:
    def __init__(self, yaml_file: str, out_dir: str):
        self._specification = yaml_file
        self._out_dir = out_dir

    def generate(self):
        cnl = YAMLReader().read_specification(self._specification)
        grammar_writer = LarkGrammarWriter()
        for lang in cnl.get_languages():
            with open(os.path.join(self._out_dir, f'grammar_{lang}.lark'), 'w') as out:
                out.write(cnl.print(lang, grammar_writer))
            py_file = os.path.join(self._out_dir, f'py_{lang}.py')
            py_writer = PythonFunctionWriter()
            if os.path.exists(py_file):
                py_writer.import_fn(py_file)
            py_writer.write(cnl.print(lang, py_writer), py_file)

                    