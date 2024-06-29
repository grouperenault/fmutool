import importlib.util
import inspect
import os
import glob
from .version import __author__ as author
from .fmu_operations import OperationAbstract


class OperationGenericCheck(OperationAbstract):
    SUPPORTED_FMI_VERSIONS = ('2.0',)

    def __init__(self):
        pass

    def __repr__(self):
        return f"FMU Generic Conformity Checks"

    def fmi_attrs(self, attrs):
        if attrs['fmiVersion'] not in self.SUPPORTED_FMI_VERSIONS:
            print(f"ERROR: fmutool only support FMI {','.join(self.SUPPORTED_FMI_VERSIONS)} versions.")

    def closure(self):
        print(f"The modelDescription.xml was parsed successfully. \n"
              f"Note that the compliance with FMI specification is not checked.")


checker_operation_list = [OperationGenericCheck()]


def _add_checkers_from_file(checker_filename: str):
    spec = importlib.util.spec_from_file_location(checker_filename, checker_filename)
    if not spec:
        print(f"ERROR: Cannot load {checker_filename}. Is this a python file?")
        return
    try:
        checker_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_module)
        for checker_name, checker_class in inspect.getmembers(checker_module, inspect.isclass):
            if OperationAbstract in checker_class.__bases__:
                checker_operation_list.append(checker_class())
                print(f"Adding checker: {checker_filename}|{checker_name}")

    except AttributeError:
        print(f"ERROR: {checker_filename} should implement class 'OperationCheck'")


def _add_checkers(variable_name: str):
    checkers_folder = os.getenv(variable_name)
    if checkers_folder:
        if os.path.isdir(checkers_folder):
            for filename in glob.glob(os.path.join(checkers_folder, "*.py")):
                _add_checkers_from_file(filename)
        else:
            print(f"ERROR: {variable_name} should point to a valid folder.")


_add_checkers("FMUTOOL_CHECKER_DIR")
