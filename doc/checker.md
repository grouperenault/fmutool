# FMU Checker

`fmutool` comes with a (very) basic checker. You can invoke it with `-check` option or with dedicated button in the GUI.

## Add your own checker

### Write your own checker

In `fmutool` a checker is written as a class derived from `OperationAbstract`.
You can use `OperationGenericCheck` as model. Your class can be stored in python file stored anywhere.
Every class derived from `OperationAbstract` will be considered as a checker and will be run during checks runtime.


### Run `fmutool` with your checker

In order to let `fmutool` know where the file implementing your checker are, you can use `fmutool.checker.add_from_file` 
function before invoking `fmutool`. The pointed file may contain multiple classes derivative from `OperationAbstract`.
All of them will be run during the checks runtime.
