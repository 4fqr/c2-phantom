#ifndef INLINE_HOOKS_H
#define INLINE_HOOKS_H

#include <stdint.h>
#include <stddef.h>

#ifdef _WIN32

// Hook structure
typedef struct _HOOK_ENTRY {
    void* target_function;
    void* detour_function;
    void* original_bytes;
    size_t hook_size;
    int active;
} HOOK_ENTRY;

// Initialize hooking engine
int hook_engine_init(void);
void hook_engine_cleanup(void);

// Install inline hook (JMP-based)
int hook_install(void* target, void* detour, HOOK_ENTRY** out_hook);

// Remove hook and restore original bytes
int hook_remove(HOOK_ENTRY* hook);

// Trampoline-based hooking (preserve original function)
int hook_install_trampoline(void* target, void* detour, void** original_func, HOOK_ENTRY** out_hook);

// Hook Windows API functions
int hook_api_function(const char* module, const char* function, void* detour, HOOK_ENTRY** out_hook);

#endif // _WIN32

#endif // INLINE_HOOKS_H
