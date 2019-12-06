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
from sbml_utils import of_valid_types, Switch

class Node(ABC):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f'args is {self.args} and kwargs is {self.kwargs}'

    @abstractmethod
    def evaluate(self):
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

    def evaluate(self):
        for line in self.statements:
            print(line.evaluate())


class ExpressionNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self):
        op = self.kwargs.get('operator')
        if op is None:
            return self.args[0]

        self.args = evaluate_nodes(self.args)
        with Switch(op) as case:
            if case(Operator.ORELSE):
                if of_valid_types(self.args, [[bool]]):
                    return functools.reduce(operator.or_, self.args)
                raise SemanticError()
            elif case(Operator.ANDALSO):
                if of_valid_types(self.args, [[bool]]):
                    return functools.reduce(operator.and_, self.args)
                raise SemanticError()
            elif case(Operator.NOT):
                if of_valid_types(self.args, [[bool]]): 
                    return not self.args[0]
                raise SemanticError()

            elif case(Operator.LESS_THAN):
                if of_valid_types(self.args, [[int, float], [str]]):
                    return functools.reduce(operator.lt, self.args)
                raise SemanticError()
            elif case(Operator.LESS_EQUAL):
                if of_valid_types(self.args, [[int, float], [str]]):
                    return functools.reduce(operator.le, self.args)
                raise SemanticError()
            elif case(Operator.GREATER_THAN):
                if of_valid_types(self.args, [[int, float], [str]]):
                    return functools.reduce(operator.gt, self.args)
                raise SemanticError()
            elif case(Operator.GREATER_EQUAL):
                if of_valid_types(self.args, [[int, float], [str]]):
                    return functools.reduce(operator.ge, self.args)
                raise SemanticError()
            elif case(Operator.EQUAL):
                if of_valid_types(self.args, [[int, float], [str]]):
                    return functools.reduce(operator.eq, self.args)
                raise SemanticError()
            elif case(Operator.NOT_EQUAL):
                if of_valid_types(self.args, [[int, float], [str]]):
                    return functools.reduce(operator.ne, self.args)
                raise SemanticError()

            elif case(Operator.CONS):
                if of_valid_types([self.args[1]], [list]):
                    self.args[1].insert(0, self.args[0])
                    return self.args[1]
                raise SemanticError()
            elif case(Operator.IN):
                if of_valid_types([self.args[1]], [[list]]) or \
                   of_valid_types(self.args, [[str]]):
                    return self.args[0] in self.args[1]
                raise SemanticError()
            
            elif case(Operator.PLUS):
                if of_valid_types(self.args, [[int, float], [str], [list]]):
                    return functools.reduce(operator.add, self.args)
                raise SemanticError()
            elif case(Operator.MINUS):
                if of_valid_types(self.args, [[int, float]]):
                    return functools.reduce(operator.sub, self.args)
                raise SemanticError()
            elif case(Operator.TIMES):
                if of_valid_types(self.args, [[int, float]]):
                    return functools.reduce(operator.mul, self.args)
                raise SemanticError()
            elif case(Operator.DIVIDE):
                if of_valid_types(self.args, [[int, float]]):
                    return functools.reduce(operator.truediv, self.args)
                raise SemanticError()
            elif case(Operator.DIV):
                if of_valid_types(self.args, [[int]]):
                    return functools.reduce(operator.floordiv, self.args)
                raise SemanticError()
            elif case(Operator.MOD):
                if of_valid_types(self.args, [[int]]):
                    return functools.reduce(operator.mod, self.args)
                raise SemanticError()
            elif case(Operator.EXPONENT):
                if of_valid_types(self.args, [[int, float]]):
                    return functools.reduce(operator.pow, self.args)
                raise SemanticError()

            elif case(Operator.LBRACKET):
                if of_valid_types([self.args[0]], [[list, str]]) and \
                   of_valid_types([self.args[1]], [[int]]) and \
                   0 <= self.args[1] < len(self.args[0]):
                    return self.args[0][self.args[1]]
                raise SemanticError()
            elif case(Operator.TUPLE_INDEX):
                if of_valid_types([self.args[0]], [[int]]) and \
                   of_valid_types([self.args[1]], [[tuple]]) and \
                   0 < self.args[0] <= len(self.args[1]):
                    return self.args[1][self.args[0] - 1]
                raise SemanticError()

            raise RuntimeError('Case not handled')


class ConditionNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self):
        keyword = self.kwargs.get('keyword')
        with Switch(keyword) as case:
            if case(Keyword.IF):
                condition = self.args[0].evaluate()
                if of_valid_types([condition], [[bool]]):
                    if condition: 
                        return self.args[1].evaluate()
                    return None
                raise SemanticError()
            elif case(Keyword.IF + Keyword.ELSE):
                condition = self.args[0].evaluate()
                if of_valid_types([condition], [[bool]]):
                    if condition:
                        return self.args[1].evaluate()
                    return self.args[2].evaluate()
                raise SemanticError()
            elif case(Keyword.WHILE):
                condition = self.args[0].evaluate()
                if of_valid_types([condition], [[bool]]):
                    while self.args[0].evaluate():
                        print(self.args[1].evaluate())

                        condition = self.args[0].evaluate()
                        if not of_valid_types([condition], [[bool]]):
                            break
                    else:
                        return None
                raise SemanticError()
            raise RuntimeError('Case not handled')
    

class StatementNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self):
        keyword = self.kwargs.get('keyword')
        with Switch(keyword) as case:
            if case(Keyword.PRINT):
                print(self.args[0].evaluate())
                return
            raise RuntimeError('Case not handled')
    

class CollectionNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        elements = evaluate_nodes(args)
        self.items = elements

    def prepend_item(self, item):
        self.items.insert(0, evaluate_node(item))
        return self

    def append_item(self, item):
        self.items.append(evaluate_node(item))
        return self

    def evaluate(self):
        collection_type = self.kwargs.get('type')
        with Switch(collection_type) as case:
            if case(tuple):
                items = ()
                for elem in self.items:
                    items += (elem,)
                return items
            elif case(list):
                return self.items
            raise RuntimeError('Case not handled')


def evaluate_nodes(nodes):
    return [evaluate_node(node) for node in nodes]


def evaluate_node(node):
    return node.evaluate() if isinstance(node, Node) else node
