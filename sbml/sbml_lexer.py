import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


import ply.lex as lex
import re
from sbml_enums import Keyword, Operator, Type


keyword_tokens = [token.name for token in Keyword]
operator_tokens = [token.name for token in Operator]
type_tokens = [token.name for token in Type]
tokens = keyword_tokens + operator_tokens + type_tokens


t_ignore = ' \t'


t_IF = re.escape(Keyword.IF.value)
t_ELSE = re.escape(Keyword.ELSE.value)

t_WHILE = re.escape(Keyword.WHILE.value)

t_PRINT = re.escape(Keyword.PRINT.value)


t_LPAREN = re.escape(Operator.LPAREN.value)
t_RPAREN = re.escape(Operator.RPAREN.value)
t_LBRACKET = re.escape(Operator.LBRACKET.value)
t_RBRACKET = re.escape(Operator.RBRACKET.value)
t_LBRACE = re.escape(Operator.LBRACE.value)
t_RBRACE = re.escape(Operator.RBRACE.value)
t_COMMA = re.escape(Operator.COMMA.value)
t_SEMICOLON = re.escape(Operator.SEMICOLON.value)
t_TAKES_VALUE = re.escape(Operator.TAKES_VALUE.value)

t_TUPLE_INDEX = re.escape(Operator.TUPLE_INDEX.value)

t_EXPONENT = re.escape(Operator.EXPONENT.value)

t_DIVIDE = re.escape(Operator.DIVIDE.value)
t_DIV = re.escape(Operator.DIV.value)
t_MOD = re.escape(Operator.MOD.value)
t_TIMES = re.escape(Operator.TIMES.value)

t_PLUS = re.escape(Operator.PLUS.value)
t_MINUS = re.escape(Operator.MINUS.value)

t_IN = re.escape(Operator.IN.value)

t_CONS = re.escape(Operator.CONS.value)

t_LESS_THAN = re.escape(Operator.LESS_THAN.value)
t_GREATER_THAN = re.escape(Operator.GREATER_THAN.value)
t_LESS_EQUAL = re.escape(Operator.LESS_EQUAL.value)
t_GREATER_EQUAL = re.escape(Operator.GREATER_EQUAL.value)
t_EQUAL = re.escape(Operator.EQUAL.value)
t_NOT_EQUAL = re.escape(Operator.NOT_EQUAL.value)
t_NOT_EQUAL_ALT = re.escape(Operator.NOT_EQUAL_ALT.value)

t_NOT = re.escape(Operator.NOT.value)

t_ANDALSO = re.escape(Operator.ANDALSO.value)

t_ORELSE = re.escape(Operator.ORELSE.value)


@lex.TOKEN(Type.REAL.value)
def t_REAL(t):
    t.value = float(t.value)
    return t


@lex.TOKEN(Type.INTEGER.value)
def t_INTEGER(t):
    t.value = int(t.value)
    return t


@lex.TOKEN(Type.BOOLEAN.value)
def t_BOOLEAN(t):
    t.value = t.value == 'True'
    return t


@lex.TOKEN(Type.STRING.value)
def t_STRING(t):
    t.value = t.value[1:-1]
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_comment(t):
    r'//.*'
    pass


def t_error(t):
    t.lexer.skip(1)
    raise SyntaxError('Syntax Error')


def analyze():
    lex.lex()
