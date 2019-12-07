import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


import sbml_parser
from sbml_errors import SemanticError


def main():
    if len(sys.argv) != 2:
        print('usage: python3 sbml.py <file>')
        sys.exit(1)

    filename = sys.argv[1]
    parser = sbml_parser.get_parser()
    with open(filename, 'r') as file_handler:
        try:
            file_content = file_handler.read()
            symbol_table = {}
            ast = parser.parse(file_content)
            ast.evaluate(symbol_table)
        except SyntaxError as e:
            print(e)
        except SemanticError as e:
            print(e)
        except RuntimeError as e:
            # This scenario should never happen
            print(e)
            raise e


if '__main__' == __name__:
    main()
