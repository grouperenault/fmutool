from fmutool.version import __author__ as author

from .fmu_operations import OperationAbstract, OperationException


class OperationCheck(OperationAbstract):
    def __init__(self):
        pass

    def __repr__(self):
        return f"FMU Conformity Checks according to local rules."


    def closure(self):
        print(f"Check rules are not shipped with this open-source implementation.\n"
              f"If interested in this topic you may contact {author}.")
