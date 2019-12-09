import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


import ply.lex as lex
import re
from sbml_enums import Keyword, Operator, Type
from sbml_errors import SyntaxError
from sbml_utils import is_identifier


reserved_tokens = {
    kw.value: kw.name for kw in Keyword if is_identifier(kw, is_token=True)
}
reserved_tokens.update({
    op.value: op.name for op in Operator if is_identifier(op, is_token=True)
})
reserved_tokens.update({
    t.value: t.name for t in Type if is_identifier(t, is_token=True)
})

extra_op_tokens = [
    token.name for token in Operator if not is_identifier(token, is_token=True)
]
extra_type_tokens = [
    token.name for token in Type if not is_identifier(token, is_token=True)
]
tokens = list(reserved_tokens.values()) + extra_op_tokens + extra_type_tokens


t_ignore = ' \t'


t_LPAREN = re.escape(Operator.LPAREN.value)
t_RPAREN = re.escape(Operator.RPAREN.value)
t_LBRACKET = re.escape(Operator.LBRACKET.value)
t_RBRACKET = re.escape(Operator.RBRACKET.value)
t_LBRACE = re.escape(Operator.LBRACE.value)
t_RBRACE = re.escape(Operator.RBRACE.value)
t_COMMA = re.escape(Operator.COMMA.value)
t_SEMICOLON = re.escape(Operator.SEMICOLON.value)

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

t_NOT = re.escape(Operator.NOT.value)

t_ANDALSO = re.escape(Operator.ANDALSO.value)

t_ORELSE = re.escape(Operator.ORELSE.value)

# Has to be after t_EQUAL as it's shorter in length
t_TAKES_VALUE = re.escape(Operator.TAKES_VALUE.value)


@lex.TOKEN(Type.REAL.value)
def t_REAL(t):
    t.value = float(t.value)
    return t


@lex.TOKEN(Type.INTEGER.value)
def t_INTEGER(t):
    t.value = int(t.value)
    return t


@lex.TOKEN(Type.STRING.value)
def t_STRING(t):
    return t


@lex.TOKEN(Type.IDENTIFIER.value)
def t_IDENTIFIER(t):
    t.type = reserved_tokens.get(t.value, Type.IDENTIFIER.name)

    # Take care of boolean here as they are also reserved words that falls
    # under the general variable regex
    if t.value == 'True' or t.value == 'False':
        t.type = 'BOOLEAN'
        t.value = t.value == 'True'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_comment(t):
    r'//.*'
    pass


def t_error(t):
    t.lexer.skip(1)
    raise SyntaxError


def analyze():
    lex.lex()
