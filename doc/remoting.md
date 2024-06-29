# Remoting

## What is it ?

The remoting feature lets you to add an additional interface to an existing FMU.
There is 3 use cases:
1. Add a different bitness interface. For example, add a Windows 64bits interface to a existing 32bits only FMU.
2. Encapsulate the DLL of an existing FMU inside a dedicated process. This process will communicate with the simulation 
master.
3. Add a different OS interface. This feature is under study.


## Limitation

Currently, only Co-simulation mode for FMI 2.0 is supported.


## Available  configurations

| FMU \ master   | Windows 32bits        | Windows 64bits        | Linux 32bit                           | Linux 64bits                          |   
|----------------|-----------------------|-----------------------|---------------------------------------|---------------------------------------|
| Windows 32bits | `-add-frontend-win32` | `-add-remoting-win64` | -                                     | -                                     |
| Windows 64bits | `-add-remoting-win32` | `-add-frontend-win64` | -                                     | -                                     |
| Linux 32bits   | -                     | -                     | See `OperationAddRemotingWinAbstract` | See `OperationAddRemotingWinAbstract` |
| Linux 64bits   | -                     | -                     | See `OperationAddRemotingWinAbstract` | See `OperationAddRemotingWinAbstract` |
