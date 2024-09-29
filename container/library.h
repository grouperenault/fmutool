/*
 * 2022-2024 Nicolas.LAURENT@Renault.com
 * 
 * DLL/SO loading functions.
 */

#ifndef LIBRARY_H
#define LIBRARY_H

#	ifdef __cplusplus
extern "C" {
#	endif

#ifdef WIN32
#	include <Windows.h>
#endif

/*----------------------------------------------------------------------------
                              L I B R A R Y _ T
----------------------------------------------------------------------------*/

#ifdef WIN32
typedef HINSTANCE library_t;
#else
typedef void* library_t;
#endif


/*----------------------------------------------------------------------------
                        L I B R A R Y _ S T A T U S _ T
----------------------------------------------------------------------------*/

#ifdef WIN32
typedef enum {
    LIBRARY_DLL_NOT_FOUND,
    LIBRARY_DLL_MISSING_DEPENDENCIES,
    LIBRARY_DLL_OK
} libray_status_t;
#endif


/*----------------------------------------------------------------------------
                             P R O T O T Y P E S
----------------------------------------------------------------------------*/

extern void* library_symbol(library_t library, const char *symbol_name);
extern library_t library_load(const char* library_filename);
extern void library_unload(library_t library);

#	ifdef __cplusplus
}
#	endif

#endif
