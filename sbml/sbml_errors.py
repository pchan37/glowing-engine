import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


class SemanticError(RuntimeError):

    def __init__(self):
        super().__init__('SEMANTIC ERROR')


class SyntaxError(SyntaxError):

    def __init__(self):
        super().__init__('SYNTAX ERROR')
