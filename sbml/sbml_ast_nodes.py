import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


import functools
import operator
from abc import ABC, abstractmethod
from sbml_enums import Keyword, Operator
from sbml_errors import SemanticError
from sbml_utils import is_identifier, is_string, of_valid_types, Switch

class Node(ABC):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f'args is {self.args} and kwargs is {self.kwargs}'

    @abstractmethod
    def evaluate(self, symbol_table):
        pass


class BlockNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statements = list(args)

    def prepend_statement(self, statement):
        self.statements.insert(0, statement)
        return self

    def append_statement(self, statement):
        self.statements.append(statement)
        return self

    def evaluate(self, symbol_table):
        for line in self.statements:
            evaluate_node(line, symbol_table)


class ExpressionNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self, symbol_table):
        op = self.kwargs.get('operator')
        if op is None:
            if is_string(self.args[0]):
                return self.args[0][1:-1]
            return self.args[0]

        args = evaluate_nodes(self.args, symbol_table)
        with Switch(op) as case:
            if case(Operator.ORELSE):
                if of_valid_types(args, [[bool]]):
                    return functools.reduce(operator.or_, args)
                raise SemanticError()
            elif case(Operator.ANDALSO):
                if of_valid_types(args, [[bool]]):
                    return functools.reduce(operator.and_, args)
                raise SemanticError()
            elif case(Operator.NOT):
                if of_valid_types(args, [[bool]]): 
                    return not args[0]
                raise SemanticError()

            elif case(Operator.LESS_THAN):
                if of_valid_types(args, [[int, float], [str]]):
                    return functools.reduce(operator.lt, args)
                raise SemanticError()
            elif case(Operator.LESS_EQUAL):
                if of_valid_types(args, [[int, float], [str]]):
                    return functools.reduce(operator.le, args)
                raise SemanticError()
            elif case(Operator.GREATER_THAN):
                if of_valid_types(args, [[int, float], [str]]):
                    return functools.reduce(operator.gt, args)
                raise SemanticError()
            elif case(Operator.GREATER_EQUAL):
                if of_valid_types(args, [[int, float], [str]]):
                    return functools.reduce(operator.ge, args)
                raise SemanticError()
            elif case(Operator.EQUAL):
                if of_valid_types(args, [[int, float], [str]]):
                    return functools.reduce(operator.eq, args)
                raise SemanticError()
            elif case(Operator.NOT_EQUAL):
                if of_valid_types(args, [[int, float], [str]]):
                    return functools.reduce(operator.ne, args)
                raise SemanticError()

            elif case(Operator.CONS):
                if of_valid_types([args[1]], [[list]]):
                    args[1].insert(0, args[0])
                    return args[1]
                raise SemanticError()
            elif case(Operator.IN):
                if of_valid_types([args[1]], [[list]]) or \
                   of_valid_types(args, [[str]]):
                    return args[0] in args[1]
                raise SemanticError()
            
            elif case(Operator.PLUS):
                if of_valid_types(args, [[int, float], [str], [list]]):
                    return functools.reduce(operator.add, args)
                raise SemanticError()
            elif case(Operator.MINUS):
                if of_valid_types(args, [[int, float]]):
                    return functools.reduce(operator.sub, args)
                raise SemanticError()
            elif case(Operator.TIMES):
                if of_valid_types(args, [[int, float]]):
                    return functools.reduce(operator.mul, args)
                raise SemanticError()
            elif case(Operator.DIVIDE):
                if of_valid_types(args, [[int, float]]):
                    return functools.reduce(operator.truediv, args)
                raise SemanticError()
            elif case(Operator.DIV):
                if of_valid_types(args, [[int]]):
                    return functools.reduce(operator.floordiv, args)
                raise SemanticError()
            elif case(Operator.MOD):
                if of_valid_types(args, [[int]]):
                    return functools.reduce(operator.mod, args)
                raise SemanticError()
            elif case(Operator.EXPONENT):
                if of_valid_types(args, [[int, float]]):
                    return functools.reduce(operator.pow, args)
                raise SemanticError()

            elif case(Operator.LBRACKET):
                if of_valid_types([args[0]], [[list, str]]) and \
                   of_valid_types([args[1]], [[int]]) and \
                   0 <= args[1] < len(args[0]):
                    return args[0][args[1]]
                raise SemanticError()
            elif case(Operator.TUPLE_INDEX):
                if of_valid_types([args[0]], [[int]]) and \
                   of_valid_types([args[1]], [[tuple]]) and \
                   0 < args[0] <= len(args[1]):
                    return args[1][args[0] - 1]
                raise SemanticError()

            raise RuntimeError('Case not handled')


class ConditionNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self, symbol_table):
        keyword = self.kwargs.get('keyword')
        with Switch(keyword) as case:
            if case(Keyword.IF):
                condition = self.args[0].evaluate(symbol_table)
                if of_valid_types([condition], [[bool]]):
                    if condition: 
                        return evaluate_node(self.args[1], symbol_table)
                    return None
                raise SemanticError()
            elif case(Keyword.IF + Keyword.ELSE):
                condition = self.args[0].evaluate(symbol_table)
                if of_valid_types([condition], [[bool]]):
                    if condition:
                        return evaluate_node(self.args[1], symbol_table)
                    return evaluate_node(self.args[2], symbol_table)
                raise SemanticError()
            elif case(Keyword.WHILE):
                condition = evaluate_node(self.args[0], symbol_table)
                if of_valid_types([condition], [[bool]]):
                    while condition:
                        evaluate_node(self.args[1], symbol_table)

                        condition = evaluate_node(self.args[0], symbol_table)
                        if not of_valid_types([condition], [[bool]]):
                            break
                    else:
                        return None
                raise SemanticError()
            raise RuntimeError('Case not handled')
    

class StatementNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self, symbol_table):
        keyword = self.kwargs.get('keyword')
        with Switch(keyword) as case:
            if case(Keyword.PRINT):
                expression = evaluate_node(self.args[0], symbol_table)
                print(expression)
                return
            elif case(Operator.TAKES_VALUE):
                if len(self.args) == 2:
                    symbol = self.args[0]
                    value = evaluate_node(self.args[1], symbol_table)
                    symbol_table[symbol] = value
                    return
                elif len(self.args) == 3:
                    if is_identifier(self.args[0]):
                        symbol = self.args[0]
                        index = evaluate_node(self.args[1], symbol_table) 
                        value = evaluate_node(self.args[2], symbol_table) 

                        array = evaluate_node(VariableNode(symbol), symbol_table)
                        array[index] = value
                        symbol_table[symbol] = array;
                        return
                    else:
                        self.args = evaluate_nodes(self.args, symbol_table)
                        symbol, index, value = self.args

                        symbol[index] = value
                        return
            raise RuntimeError('Case not handled')
    

class CollectionNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = list(args) if args is not None else []

    def prepend_item(self, item):
        self.items.insert(0, item)
        return self

    def append_item(self, item):
        self.items.append(item)
        return self

    def evaluate(self, symbol_table):
        collection_type = self.kwargs.get('type')
        with Switch(collection_type) as case:
            if case(tuple):
                items = ()
                for elem in self.items:
                    items += (evaluate_node(elem, symbol_table),)
                return items
            elif case(list):
                return evaluate_nodes(self.items, symbol_table)
            raise RuntimeError('Case not handled')


class VariableNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self, symbol_table):
        if self.args[0] in symbol_table:
            return symbol_table[self.args[0]]
        raise SemanticError()


def evaluate_nodes(nodes, symbol_table):
    return [evaluate_node(node, symbol_table) for node in nodes]


def evaluate_node(node, symbol_table):
    return node.evaluate(symbol_table) if isinstance(node, Node) else node
