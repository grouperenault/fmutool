#ifndef LOGGER_H
#   define LOGGER_H

#include "fmi2Functions.h"

#include "container.h"


/*----------------------------------------------------------------------------
                            P R O T O T Y P E S
----------------------------------------------------------------------------*/

void logger(const container_t *container, fmi2Status status, const char *message, ...);
void logger_embedded_fmu(fmu_t *fmu,
                         fmi2String instanceName, fmi2Status status,
                         fmi2String category, fmi2String message, ...);

#endif