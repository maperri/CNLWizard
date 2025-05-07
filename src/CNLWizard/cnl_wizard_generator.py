import os

from CNLWizard.reader import YAMLReader, pyReader
from CNLWizard.writer import LarkGrammarWriter, PythonFunctionWriter


class CnlWizardGenerator:
    def __init__(self, yaml_file: str, import_dirs: list[str], out_dir: str):
        self._specification = yaml_file
        if import_dirs is None:
            import_dirs = []
        self._imported_libs = self._get_imported_grammars(import_dirs)
        self._imported_fn = self._get_imported_functions(import_dirs)
        self._out_dir = out_dir

    def _import_internal_lib(self):
        return YAMLReader().read_specification(
            os.path.join(os.path.join(os.path.dirname(__file__), 'libs', 'cnl_wizard_propositions.yaml')))

    def _is_specification_file(self, file: str) -> bool:
        if os.path.splitext(file)[1] == '.yaml':
            return True
        return False

    def _is_py_file(self, file: str) -> bool:
        if os.path.splitext(file)[1] == '.py':
            return True
        return False

    def _get_filename(self, file: str) -> str:
        return os.path.splitext(file)[0]

    def _get_imported_grammars(self, import_dirs: list[str]) -> dict:
        res = {'cnl_wizard': self._import_internal_lib()}
        for import_dir in import_dirs:
            for file in os.listdir(import_dir):
                if self._is_specification_file(file):
                    res[self._get_filename(file)] = YAMLReader().read_specification(os.path.join(import_dir, file))
        return res

    def _import_internal_fn(self):
        res = {}
        for file in os.listdir(os.path.join(os.path.dirname(__file__), 'libs')):
            if self._is_py_file(file):
                res[self._get_filename(file)] = pyReader().get_functions(
                    os.path.join(os.path.dirname(__file__), 'libs', file))
        return res

    def _get_imported_functions(self, import_dirs: list[str]) -> dict:
        res = {'cnl_wizard': self._import_internal_fn()}
        for import_dir in import_dirs:
            yaml_file_name = ''
            functions = {}
            for file in os.listdir(import_dir):
                if self._is_specification_file(file):
                    yaml_file_name = self._get_filename(file)
                if self._is_py_file(file):
                    PY_FILE_PREFIX = 'py_'
                    functions[self._get_filename(file).removeprefix(PY_FILE_PREFIX)] = pyReader().get_functions(os.path.join(import_dir, file))
            res[yaml_file_name] = functions
        return res

    def generate(self):
        cnl = YAMLReader(self._imported_libs).read_specification(self._specification)
        grammar_writer = LarkGrammarWriter()
        for lang in cnl.get_languages():
            with open(os.path.join(self._out_dir, f'grammar_{lang}.lark'), 'w') as out:
                out.write(cnl.print(lang, grammar_writer))
            py_file = os.path.join(self._out_dir, f'py_{lang}.py')
            py_writer = PythonFunctionWriter(self._imported_fn)
            if os.path.exists(py_file):
                py_writer.import_fn(py_file)
            py_writer.write(cnl.print(lang, py_writer), py_file)

