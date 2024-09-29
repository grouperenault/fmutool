/*
 * 2022-2024 Nicolas.LAURENT@Renault.com
 *
 * DLL/SO loading functions.
 */

#ifdef WIN32
#	include <windows.h>
#else
#	include <dlfcn.h>
#   include <unistd.h> 
#endif

#include "library.h"


void *library_symbol(library_t library, const char *symbol_name) {
#ifdef WIN32
	return (void *)GetProcAddress(library, symbol_name);
#else
	return dlsym(library, symbol_name);
#endif
}


library_t library_load(const char* library_filename) {
	library_t handle;
#ifdef WIN32
	handle = LoadLibraryA(library_filename);
#else
	handle = dlopen(library_filename, RTLD_LAZY);	/* RTLD_LOCAL can lead to failure */
#endif
	return handle;
}


void library_unload(library_t library) {
	if (library) {
#ifdef WIN32
		FreeLibrary(library);
#else
		dlclose(library);
#endif
	}
}

