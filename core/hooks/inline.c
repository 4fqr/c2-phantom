#ifdef _WIN32

#include "inline.h"
#include <windows.h>
#include <stdio.h>
#include <string.h>

#define MAX_HOOKS 128

static HOOK_ENTRY hook_table[MAX_HOOKS] = {0};
static int hook_count = 0;

int hook_engine_init(void) {
    memset(hook_table, 0, sizeof(hook_table));
    hook_count = 0;
    return 0;
}

void hook_engine_cleanup(void) {
    for (int i = 0; i < hook_count; i++) {
        if (hook_table[i].active) {
            hook_remove(&hook_table[i]);
        }
    }
    hook_count = 0;
}

// Calculate minimum instruction length for hook
static size_t calculate_hook_length(unsigned char* code, size_t min_length) {
    size_t length = 0;
    
    // Simple x64 instruction length heuristic
    while (length < min_length) {
        unsigned char opcode = code[length];
        
        // Handle REX prefix
        if ((opcode & 0xF0) == 0x40) {
            length++;
            opcode = code[length];
        }
        
        // Common instruction patterns
        if (opcode == 0x48 || opcode == 0x4C) { // mov, lea, etc
            length += 3;
        } else if (opcode == 0xB8) { // mov eax, imm32
            length += 5;
        } else if (opcode == 0xE9) { // jmp near
            length += 5;
        } else if (opcode == 0xFF) { // indirect call/jmp
            length += 6;
        } else {
            length += 2; // Default
        }
    }
    
    return length;
}

int hook_install(void* target, void* detour, HOOK_ENTRY** out_hook) {
    if (hook_count >= MAX_HOOKS) return -1;
    
    HOOK_ENTRY* hook = &hook_table[hook_count++];
    
    // x64 JMP instruction: FF 25 00 00 00 00 <8-byte address>
    hook->hook_size = 14; // JMP takes 14 bytes on x64
    
    // Backup original bytes
    hook->original_bytes = malloc(hook->hook_size);
    if (!hook->original_bytes) return -1;
    
    memcpy(hook->original_bytes, target, hook->hook_size);
    
    // Build JMP to detour
    unsigned char jmp_patch[14] = {
        0xFF, 0x25, 0x00, 0x00, 0x00, 0x00,  // jmp qword ptr [rip+0]
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00  // 8-byte address
    };
    
    *(void**)(jmp_patch + 6) = detour;
    
    // Make target writable
    DWORD old_protect;
    if (!VirtualProtect(target, hook->hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        free(hook->original_bytes);
        return -1;
    }
    
    // Install hook
    memcpy(target, jmp_patch, hook->hook_size);
    
    // Restore protection
    DWORD temp;
    VirtualProtect(target, hook->hook_size, old_protect, &temp);
    
    hook->target_function = target;
    hook->detour_function = detour;
    hook->active = 1;
    
    if (out_hook) *out_hook = hook;
    
    return 0;
}

int hook_remove(HOOK_ENTRY* hook) {
    if (!hook || !hook->active) return -1;
    
    // Make target writable
    DWORD old_protect;
    if (!VirtualProtect(hook->target_function, hook->hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        return -1;
    }
    
    // Restore original bytes
    memcpy(hook->target_function, hook->original_bytes, hook->hook_size);
    
    // Restore protection
    DWORD temp;
    VirtualProtect(hook->target_function, hook->hook_size, old_protect, &temp);
    
    free(hook->original_bytes);
    hook->active = 0;
    
    return 0;
}

int hook_install_trampoline(void* target, void* detour, void** original_func, HOOK_ENTRY** out_hook) {
    if (hook_count >= MAX_HOOKS) return -1;
    
    HOOK_ENTRY* hook = &hook_table[hook_count++];
    
    // Calculate how many bytes we need to steal
    size_t min_hook_size = 14; // JMP on x64
    hook->hook_size = calculate_hook_length((unsigned char*)target, min_hook_size);
    
    // Allocate trampoline (original bytes + jmp back)
    size_t trampoline_size = hook->hook_size + 14;
    void* trampoline = VirtualAlloc(NULL, trampoline_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!trampoline) return -1;
    
    // Copy stolen bytes to trampoline
    memcpy(trampoline, target, hook->hook_size);
    
    // Add JMP back to (target + hook_size)
    unsigned char jmp_back[14] = {
        0xFF, 0x25, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    *(void**)(jmp_back + 6) = (unsigned char*)target + hook->hook_size;
    memcpy((unsigned char*)trampoline + hook->hook_size, jmp_back, 14);
    
    // Backup original bytes
    hook->original_bytes = malloc(hook->hook_size);
    if (!hook->original_bytes) {
        VirtualFree(trampoline, 0, MEM_RELEASE);
        return -1;
    }
    memcpy(hook->original_bytes, target, hook->hook_size);
    
    // Build JMP to detour
    unsigned char jmp_detour[14] = {
        0xFF, 0x25, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    *(void**)(jmp_detour + 6) = detour;
    
    // Make target writable
    DWORD old_protect;
    if (!VirtualProtect(target, hook->hook_size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        free(hook->original_bytes);
        VirtualFree(trampoline, 0, MEM_RELEASE);
        return -1;
    }
    
    // Install hook
    memcpy(target, jmp_detour, hook->hook_size);
    
    // NOP out any remaining bytes
    if (hook->hook_size > 14) {
        memset((unsigned char*)target + 14, 0x90, hook->hook_size - 14);
    }
    
    // Restore protection
    DWORD temp;
    VirtualProtect(target, hook->hook_size, old_protect, &temp);
    
    hook->target_function = target;
    hook->detour_function = detour;
    hook->active = 1;
    
    if (out_hook) *out_hook = hook;
    if (original_func) *original_func = trampoline;
    
    return 0;
}

int hook_api_function(const char* module, const char* function, void* detour, HOOK_ENTRY** out_hook) {
    HMODULE mod = GetModuleHandleA(module);
    if (!mod) {
        mod = LoadLibraryA(module);
        if (!mod) return -1;
    }
    
    FARPROC target = GetProcAddress(mod, function);
    if (!target) return -1;
    
    return hook_install((void*)target, detour, out_hook);
}

#endif // _WIN32
