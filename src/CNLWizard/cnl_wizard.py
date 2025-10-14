import argparse
import os

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from CNLWizard.cnl_wizard_generator import CnlWizardGenerator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generate', nargs='+')
    parser.add_argument('-c', '--compile', nargs=3, help='grammar py_functions cnl_text_file')
    parser.add_argument('-i', '--to-import', nargs='+', default=[], help='folder containing the files to import')
    parser.add_argument('-l', '--lang', default=None, help='language of the cnl')
    args = parser.parse_args()
    if args.generate and args.compile:
        print("Impossible to run CNLWizard both in generate and compile mode")
        return
    if args.generate:
        if not 1 <= len(args.generate) <= 2:
            raise argparse.ArgumentTypeError(f'Argument generate requires yaml file and optionally a target folder')
        yaml_specification = args.generate[0]
        out_dir = args.generate[1] if len(args.generate) == 2 else os.path.dirname(os.path.abspath(yaml_specification))
        import_dirs = args.to_import if args.to_import else []
        CnlWizardGenerator(yaml_specification, import_dirs, out_dir, args.lang).generate()
    if args.compile:
        print("---- INIT_COMPILE -------------------------------------------------------------------------------------")
        print(CnlWizardCompiler().compile(args.compile[0], args.compile[1], args.compile[2]))
        print("---- FINE_COMPILE -------------------------------------------------------------------------------------")
    return
