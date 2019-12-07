import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


import ply.yacc as yacc
import sbml_lexer
from sbml_ast_nodes import (
    Node, BlockNode, ConditionNode, ExpressionNode, StatementNode,
    CollectionNode, VariableNode
)
from sbml_enums import Operator
from sbml_errors import SyntaxError
from sbml_utils import is_identifier


sbml_lexer.analyze()
tokens = sbml_lexer.tokens


SYMBOL_TABLE = {}


def p_start(p):
    '''
    START : BLOCK
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        raise SyntaxError()


def p_block(p):
    '''
    BLOCK : LBRACE RBRACE
          | LBRACE STATEMENT_PLUS RBRACE
    '''
    if len(p) == 3:
        p[0] = BlockNode()
    elif len(p) == 4:
        p[0] = p[2]
    else:
        raise RuntimeError('Case not handled')


def p_statement_plus(p):
    '''
    STATEMENT_PLUS : BLOCK
                   | BLOCK STATEMENT_PLUS
                   | STATEMENT
                   | STATEMENT STATEMENT_PLUS
    '''
    if len(p) == 2:
        p[0] = BlockNode(p[1])
    elif len(p) == 3:
        if type(p[2]) == BlockNode:
            p[0] = p[2].prepend_statement(p[1])
        else:
            p[0] = BlockNode(p[2]).prepend_statement(p[1])
    else:
        raise RuntimeError('Case not handled')


def p_statement(p):
    '''
    STATEMENT : OR SEMICOLON
              | IFELSE_STATEMENT
              | IF_STATEMENT
              | WHILE_STATEMENT
              | PRINT_STATEMENT
              | ASSIGNMENT_STATEMENT
    '''
    if len(p) == 3:
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError('Case not handled')


def p_ifelse(p):
    '''
    IFELSE_STATEMENT : IF LPAREN OR RPAREN BLOCK ELSE BLOCK
    '''
    if len(p) == 8:
        p[0] = ConditionNode(p[3], p[5], p[7], keyword=p[1]+p[6])
    else:
        raise RuntimeError('Case not handled')


def p_if(p):
    '''
    IF_STATEMENT : IF LPAREN OR RPAREN BLOCK
    '''
    if len(p) == 6:
        p[0] = ConditionNode(p[3], p[5], keyword=p[1])
    else:
        raise RuntimeError('Case not handled')


def p_while(p):
    '''
    WHILE_STATEMENT : WHILE LPAREN OR RPAREN BLOCK
    '''
    if len(p) == 6:
        p[0] = ConditionNode(p[3], p[5], keyword=p[1])
    else:
        raise RuntimeError('Case not handled')


def p_print(p):
    '''
    PRINT_STATEMENT : PRINT LPAREN OR RPAREN SEMICOLON
    '''
    if len(p) == 6:
        p[0] = StatementNode(p[3], keyword=p[1])
    else:
        raise RuntimeError('Case not handled')


def p_assignment(p):
    '''
    ASSIGNMENT_STATEMENT : IDENTIFIER TAKES_VALUE OR SEMICOLON
                         | IDENTIFIER LBRACKET OR RBRACKET TAKES_VALUE OR SEMICOLON
                         | LBRACKET RBRACKET LBRACKET OR RBRACKET TAKES_VALUE OR SEMICOLON
    
    '''
    if len(p) == 5:
        p[0] = StatementNode(p[1], p[3], keyword=p[2])
    elif len(p) == 8:
        p[0] = StatementNode(p[1], p[3], p[6], keyword=p[5])
    elif len(p) == 9:
        raise SemanticError()
    elif len(p) == 10:
        p[0] = StatementNode(p[2], p[5], p[8], keyword=p[7])
    else:
        raise RuntimeError()


def p_or(p):
    '''
    OR : AND
       | OR ORELSE AND
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')


def p_and(p):
    '''
    AND : NEGATION
        | AND ANDALSO NEGATION
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')
        

def p_negation(p):
    '''
    NEGATION : COMPARISON
             | NOT NEGATION
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ExpressionNode(p[2], operator=p[1])
    else:
        raise RuntimeError('Case not handled')


def p_comparison(p):
    '''
    COMPARISON : CONS_LIST
               | COMPARISON LESS_THAN CONS_LIST
               | COMPARISON LESS_EQUAL CONS_LIST
               | COMPARISON GREATER_THAN CONS_LIST
               | COMPARISON GREATER_EQUAL CONS_LIST
               | COMPARISON EQUAL CONS_LIST
               | COMPARISON NOT_EQUAL CONS_LIST
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')


def p_cons_list(p):
    '''
    CONS_LIST : MEMBERSHIP
              | MEMBERSHIP CONS CONS_LIST
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')


def p_membership(p):
    '''
    MEMBERSHIP : PLUS_MINUS
               | MEMBERSHIP IN PLUS_MINUS
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')
        

def p_plus_minus(p):
    '''
    PLUS_MINUS : MULT_DIV
               | PLUS_MINUS PLUS MULT_DIV
               | PLUS_MINUS MINUS MULT_DIV
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')


def p_mult_div(p):
    '''
    MULT_DIV : URNARY
             | MULT_DIV TIMES URNARY
             | MULT_DIV DIVIDE URNARY
             | MULT_DIV DIV URNARY
             | MULT_DIV MOD URNARY
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')


def p_urnary(p):
    '''
    URNARY : EXPONENTIATION
           | MINUS URNARY
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = ExpressionNode(0, p[2], operator=p[1])
    else:
        raise RuntimeError('Case not handled')

    
def p_exponentiation(p):
    '''
    EXPONENTIATION : LIST_STR_INDEXING
                   | LIST_STR_INDEXING EXPONENT EXPONENTIATION
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    else:
        raise RuntimeError('Case not handled')


def p_list_str_indexing(p):
    '''
    LIST_STR_INDEXING : TUPLE_INDEXING
                      | LIST_STR_INDEXING LBRACKET OR RBRACKET
                      | LIST_STR_INDEXING LBRACKET OR RBRACKET TAKES_VALUE OR
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 5:
        p[0] = ExpressionNode(p[1], p[3], operator=p[2])
    elif len(p) == 7:
        p[0] = StatementNode(p[1], p[3], p[6], keyword=p[5])
    else:
        raise RuntimeError('Case not handled')


def p_tuple_indexing(p):
    '''
    TUPLE_INDEXING : TUPLE_LIST
                   | TUPLE_INDEX INTEGER TUPLE_LIST
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = ExpressionNode(p[2], p[3], operator=p[1])
    else:
        raise RuntimeError('Case not handled')


def p_tuple_items(p):
    '''
    TUPLE_ITEMS : OR
                | OR COMMA
                | OR COMMA TUPLE_ITEMS
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = CollectionNode(p[1], type=tuple)
    elif len(p) == 4:
        if type(p[3]) == CollectionNode:
            p[0] = p[3].prepend_item(p[1])
        else:
            p[0] = CollectionNode(p[3], type=tuple).prepend_item(p[1])
    else:
        raise RuntimeError('Case not handled')


def p_list_items(p):
    '''
    LIST_ITEMS : OR
               | OR COMMA LIST_ITEMS
    '''
    if len(p) == 2:
        p[0] = CollectionNode(p[1], type=list)
    elif len(p) == 4:
        if type(p[3]) == CollectionNode:
            p[0] = p[3].prepend_item(p[1])
        else:
            p[0] = CollectionNode(p[3], type=list).prepend(p[1])
    else:
        raise RuntimeError('Case not handled')


def p_tuple_list(p):
    '''
    TUPLE_LIST : PRIMARY
               | LPAREN RPAREN
               | LBRACKET RBRACKET
               | LPAREN TUPLE_ITEMS RPAREN
               | LBRACKET LIST_ITEMS RBRACKET
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3 and p[1] == Operator.LPAREN:
        p[0] = CollectionNode(type=tuple)
    elif len(p) == 3 and p[1] == Operator.LBRACKET:
        p[0] = CollectionNode(type=list)
    elif len(p) == 4:
        p[0] = p[2]
    else:
        raise RuntimeError('Case not handled')


def p_primary(p):
    '''
    PRIMARY : BOOLEAN
            | INTEGER
            | REAL
            | STRING
            | IDENTIFIER
            | LPAREN OR RPAREN
    '''
    if len(p) == 2:
        if isinstance(p[1], Node):
            p[0] = p[1]
        elif is_identifier(p[1]):
            p[0] = VariableNode(p[1])
        else:
            p[0] = ExpressionNode(p[1])
    elif len(p) == 4:
        p[0] = p[2]
    else:
        raise RuntimeError('Case not handled')


def p_error(p):
    print(p)
    raise SyntaxError()


def get_parser():
    return yacc.yacc()
