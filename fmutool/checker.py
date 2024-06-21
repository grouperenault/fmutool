import importlib.util
import os
from .version import __author__ as author
from .fmu_operations import OperationAbstract


class GenericOperationCheck(OperationAbstract):
    def __init__(self):
        pass

    def __repr__(self):
        return f"FMU Conformity Checks according to local rules."

    def closure(self):
        print(f"Check rules are not shipped with this open-source implementation.\n"
              f"If interested in this topic you may contact {author}.")


def get_checker(variable_name: str):
    checker_filename = os.getenv(variable_name)
    if checker_filename:
        if not os.path.isfile(checker_filename):
            print(f"ERROR: {checker_filename} does not exist.")
            return GenericOperationCheck
        else:
            spec = importlib.util.spec_from_file_location("fmutool.local", checker_filename)
            if not spec:
                print(f"ERROR: Cannot load {checker_filename}. Is this a python file?")
                return GenericOperationCheck
            try:
                checker_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(checker_module)
                return checker_module.OperationCheck
            except AttributeError:
                print(f"ERROR: {checker_filename} should implement class 'OperationCheck'")
                return GenericOperationCheck
    else:
        return GenericOperationCheck


OperationCheck = get_checker("FMUTOOL_CHECKER")
