import os

from CNLWizard.reader import YAMLReader, pyReader
from CNLWizard.writer import LarkGrammarWriter, PythonFunctionWriter


class CnlWizardGenerator:
    def __init__(self, yaml_file: str, out_dir: str):
        self._specification = yaml_file
        self._out_dir = out_dir

    def generate(self):
        cnl = YAMLReader().read_specification(self._specification)
        grammarWriter = LarkGrammarWriter()
        for lang in cnl.get_languages():
            with open(os.path.join(self._out_dir, f'grammar_{lang}.lark'), 'w') as out:
                out.write(cnl.print(lang, grammarWriter))
            py_path = os.path.join(self._out_dir, f'py_{lang}.py')
            if os.path.exists(py_path):
                py_writer = PythonFunctionWriter(set(pyReader().read_module(py_path)))
                with open(os.path.join(self._out_dir, f'py_{lang}.py'), 'a') as out:
                    out.write(f'{cnl.print(lang, py_writer)}')
            else:
                py_writer = PythonFunctionWriter()
                with open(os.path.join(self._out_dir, f'py_{lang}.py'), 'w') as out:
                    libs = '\n'.join(py_writer.import_libs)
                    out.write(f'{libs}\n\n\n{cnl.print(lang, py_writer)}')
                    