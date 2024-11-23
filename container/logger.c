#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fmi2Functions.h"

#include "container.h"

void logger(const container_t *container, fmi2Status status, const char *message, ...) {
    char buffer[4096];
    va_list ap;
    va_start(ap, message);
    vsnprintf(buffer, sizeof(buffer), message, ap);
    va_end(ap);

    if ((status != fmi2OK) || (container->debug))
        container->logger(container->environment, container->instance_name, status, NULL, "%s", buffer);

    return;
}


void logger_embedded_fmu(fmu_t *fmu,
                         fmi2String instanceName, fmi2Status status,
                         fmi2String category, fmi2String message, ...) {
    const container_t *container = fmu->container;
    char buffer[4096];
    va_list ap;
    va_start(ap, message);
    vsnprintf(buffer, sizeof(buffer), message, ap);
    va_end(ap);

    if ((status != fmi2OK) || (container->debug))
        container->logger(container->environment, container->instance_name, status, NULL, "%s: %s", fmu->identifier, buffer);
    /*logger(fmu->container, status, "logger_embedded(%s, %s)", fmu->identifier, instanceName);*/

    return;
}
