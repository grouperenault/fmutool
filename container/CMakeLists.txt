#
# Nicolas.LAURENT@Renault.com
#
# To build for 64bits, use `cmake -A x64` and `cmake --config Release`
# To build for 32bits, use `cmake -A x86` and `cmake --config Release`
#

cmake_minimum_required(VERSION 3.20)
project(container C)
set (CMAKE_C_STANDARD 99)


####################
# Create CONTAINER #
####################
add_library(container SHARED
		container.c	container.h
		fmu.c		fmu.h
		library.c	library.h
		logger.c    logger.h)
set_target_properties(container PROPERTIES PREFIX "")
target_include_directories(client_sm PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../fmi
)
set_target_properties(container PROPERTIES
					  RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/../fmutool/resources/win64")
#target_compile_options(container PRIVATE /W4 /WX)

