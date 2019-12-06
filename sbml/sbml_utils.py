import os
import sys


MODULE_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
if MODULE_DIR_NAME not in sys.path:
    sys.path.insert(0, MODULE_DIR_NAME)


class Switch:

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def __call__(self, *values):
        return self.value in values


def of_valid_types(args, valid_types_list):
    for valid_types in valid_types_list:
        if type(args[0]) in valid_types:
            return all(map(lambda x: type(x) in valid_types, args))
    return False
