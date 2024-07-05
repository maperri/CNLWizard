import argparse
import os.path

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from CNLWizard.cnl_wizard_generator import CnlWizardGenerator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generate', nargs='+')
    parser.add_argument('-c', '--compile', nargs=3, help='grammar py_functions cnl_text_file')
    args = parser.parse_args()
    if args.generate:
        if not 1 <= len(args.generate) <= 2:
            raise argparse.ArgumentTypeError(f'Argument generate requires between 1 and 2 arguments')
        yaml_specification = args.generate[0]
        out_dir = args.generate[1] if len(args.generate) == 2 else os.path.dirname(os.path.abspath(yaml_specification))
        CnlWizardGenerator(yaml_specification, out_dir).generate()
    if args.compile:
        print(CnlWizardCompiler().compile(args.compile[0], args.compile[1], args.compile[2]))



if __name__ == '__main__':
    main()
