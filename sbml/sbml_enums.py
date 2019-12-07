import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


import enum


class Keyword(enum.Enum):

    IF = 'if'
    ELSE = 'else'

    WHILE = 'while'

    PRINT = 'print'

    def __add__(self, other):
        return self.value + other.value

    def __eq__(self, other):
        return self.value == other


class Operator(enum.Enum):

    LPAREN = '('
    RPAREN = ')'
    LBRACKET = '['
    RBRACKET = ']'
    LBRACE = '{'
    RBRACE = '}'
    COMMA = ','
    SEMICOLON = ';'
    TAKES_VALUE = '='

    TUPLE_INDEX = '#'

    EXPONENT = '**'

    DIVIDE = '/'
    DIV = 'div'
    MOD = 'mod'
    TIMES = '*'

    PLUS = '+'
    MINUS = '-'

    IN = 'in'

    CONS = '::'

    LESS_THAN = '<'
    GREATER_THAN = '>'
    LESS_EQUAL = '<='
    GREATER_EQUAL = '>='
    EQUAL = '=='
    NOT_EQUAL = '<>'

    NOT = 'not'

    ANDALSO = 'andalso'

    ORELSE = 'orelse'


    def __eq__(self, other):
        return self.value == other


class Type(enum.Enum):

    BOOLEAN = r'(True)|(False)'
    INTEGER = r'([0-9]([0-9])*)'
    REAL = r'(([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+))([eE][+-]?[0-9]+)?'
    STRING = r'''(\"([^\\\"]|\\.)*\")|(\'([^\\\']|\\.)*\')'''

    IDENTIFIER = r'[a-zA-Z][a-zA-Z0-9_]*' 
