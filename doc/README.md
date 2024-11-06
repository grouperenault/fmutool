## FMUTool validation plan

Flowchart of a typical usage of FMUTool:
```mermaid
flowchart LR
    fmu_in["Input FMU"]
    fmutool[["FMUTool"]]
    fmu_out["Output FMU"]
    fmu_in --> fmutool
    fmutool --> fmu_out
```

Test suite is implemented in [tests directory](../tests).

### FMU Import Compatibility information
FMUtool import supports FMI 2.0 and Co-Simulation interface.

#### Tested Exporting Tool
- Amesim 
- Simulink
- [Reference FMUs](https://github.com/modelica/Reference-FMUs)

Automated testsuite use [bouncing_ball.fmu](../tests/bouncing_ball.fmu).


### FMU Export Compatibility information
FMUTool export supports FMI 2.0 and implement Co-Simulation interface.

#### Validation Tools
- fmpy

#### Tested Importing Tools
- Amesim
- ControlBuild
- Simulink
