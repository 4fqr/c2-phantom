#ifdef _WIN32

#include "direct.h"
#include <stdio.h>
#include <string.h>

// x64 syscall stub assembly
// mov r10, rcx
// mov eax, <syscall_number>
// syscall
// ret
static unsigned char syscall_stub_template[] = {
    0x4C, 0x8B, 0xD1,              // mov r10, rcx
    0xB8, 0x00, 0x00, 0x00, 0x00,  // mov eax, syscall_number (placeholder)
    0x0F, 0x05,                    // syscall
    0xC3                           // ret
};

// Global syscall table
static SYSCALL_STUB syscall_table[32] = {0};
static int syscall_table_size = 0;

// Resolve syscall number from ntdll.dll
uint32_t syscall_resolve_number(const char* function_name) {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    if (!ntdll) return 0;

    FARPROC proc = GetProcAddress(ntdll, function_name);
    if (!proc) return 0;

    // Parse function prologue to extract syscall number
    unsigned char* code = (unsigned char*)proc;
    
    // Pattern: mov eax, <syscall_number>
    // x64: 0xB8 <4 bytes>
    if (code[0] == 0x4C && code[1] == 0x8B && code[2] == 0xD1 && code[3] == 0xB8) {
        uint32_t syscall_num = *(uint32_t*)(code + 4);
        return syscall_num;
    }

    return 0;
}

int syscall_init(void) {
    // Pre-resolve common syscalls
    const char* syscalls[] = {
        "NtAllocateVirtualMemory",
        "NtWriteVirtualMemory",
        "NtProtectVirtualMemory",
        "NtCreateThreadEx",
        "NtQuerySystemInformation",
        "NtOpenProcess",
        "NtClose",
        "NtQueryInformationProcess"
    };

    for (int i = 0; i < sizeof(syscalls) / sizeof(syscalls[0]); i++) {
        uint32_t num = syscall_resolve_number(syscalls[i]);
        if (num > 0) {
            syscall_table[syscall_table_size].syscall_number = num;
            syscall_table[syscall_table_size].function_address = NULL;
            syscall_table_size++;
        }
    }

    return syscall_table_size > 0 ? 0 : -1;
}

void syscall_cleanup(void) {
    memset(syscall_table, 0, sizeof(syscall_table));
    syscall_table_size = 0;
}

// Direct syscall to NtAllocateVirtualMemory
NTSTATUS syscall_NtAllocateVirtualMemory(
    HANDLE ProcessHandle,
    PVOID* BaseAddress,
    ULONG_PTR ZeroBits,
    PSIZE_T RegionSize,
    ULONG AllocationType,
    ULONG Protect
) {
    uint32_t syscall_num = syscall_resolve_number("NtAllocateVirtualMemory");
    if (syscall_num == 0) return 0xC0000001; // STATUS_UNSUCCESSFUL

    // Allocate RWX memory for syscall stub
    void* stub = VirtualAlloc(NULL, sizeof(syscall_stub_template), 
                              MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!stub) return 0xC0000001;

    // Copy template and patch syscall number
    memcpy(stub, syscall_stub_template, sizeof(syscall_stub_template));
    *(uint32_t*)((unsigned char*)stub + 4) = syscall_num;

    // Call the syscall
    typedef NTSTATUS (*SyscallFunc)(HANDLE, PVOID*, ULONG_PTR, PSIZE_T, ULONG, ULONG);
    SyscallFunc func = (SyscallFunc)stub;
    
    NTSTATUS status = func(ProcessHandle, BaseAddress, ZeroBits, RegionSize, AllocationType, Protect);

    VirtualFree(stub, 0, MEM_RELEASE);
    return status;
}

NTSTATUS syscall_NtWriteVirtualMemory(
    HANDLE ProcessHandle,
    PVOID BaseAddress,
    PVOID Buffer,
    SIZE_T NumberOfBytesToWrite,
    PSIZE_T NumberOfBytesWritten
) {
    uint32_t syscall_num = syscall_resolve_number("NtWriteVirtualMemory");
    if (syscall_num == 0) return 0xC0000001;

    void* stub = VirtualAlloc(NULL, sizeof(syscall_stub_template), 
                              MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!stub) return 0xC0000001;

    memcpy(stub, syscall_stub_template, sizeof(syscall_stub_template));
    *(uint32_t*)((unsigned char*)stub + 4) = syscall_num;

    typedef NTSTATUS (*SyscallFunc)(HANDLE, PVOID, PVOID, SIZE_T, PSIZE_T);
    SyscallFunc func = (SyscallFunc)stub;
    
    NTSTATUS status = func(ProcessHandle, BaseAddress, Buffer, NumberOfBytesToWrite, NumberOfBytesWritten);

    VirtualFree(stub, 0, MEM_RELEASE);
    return status;
}

NTSTATUS syscall_NtProtectVirtualMemory(
    HANDLE ProcessHandle,
    PVOID* BaseAddress,
    PSIZE_T RegionSize,
    ULONG NewProtect,
    PULONG OldProtect
) {
    uint32_t syscall_num = syscall_resolve_number("NtProtectVirtualMemory");
    if (syscall_num == 0) return 0xC0000001;

    void* stub = VirtualAlloc(NULL, sizeof(syscall_stub_template), 
                              MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!stub) return 0xC0000001;

    memcpy(stub, syscall_stub_template, sizeof(syscall_stub_template));
    *(uint32_t*)((unsigned char*)stub + 4) = syscall_num;

    typedef NTSTATUS (*SyscallFunc)(HANDLE, PVOID*, PSIZE_T, ULONG, PULONG);
    SyscallFunc func = (SyscallFunc)stub;
    
    NTSTATUS status = func(ProcessHandle, BaseAddress, RegionSize, NewProtect, OldProtect);

    VirtualFree(stub, 0, MEM_RELEASE);
    return status;
}

NTSTATUS syscall_NtCreateThreadEx(
    PHANDLE ThreadHandle,
    ACCESS_MASK DesiredAccess,
    POBJECT_ATTRIBUTES ObjectAttributes,
    HANDLE ProcessHandle,
    PVOID StartRoutine,
    PVOID Argument,
    ULONG CreateFlags,
    SIZE_T ZeroBits,
    SIZE_T StackSize,
    SIZE_T MaximumStackSize,
    PVOID AttributeList
) {
    uint32_t syscall_num = syscall_resolve_number("NtCreateThreadEx");
    if (syscall_num == 0) return 0xC0000001;

    void* stub = VirtualAlloc(NULL, sizeof(syscall_stub_template), 
                              MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!stub) return 0xC0000001;

    memcpy(stub, syscall_stub_template, sizeof(syscall_stub_template));
    *(uint32_t*)((unsigned char*)stub + 4) = syscall_num;

    typedef NTSTATUS (*SyscallFunc)(PHANDLE, ACCESS_MASK, POBJECT_ATTRIBUTES, HANDLE, PVOID, PVOID, ULONG, SIZE_T, SIZE_T, SIZE_T, PVOID);
    SyscallFunc func = (SyscallFunc)stub;
    
    NTSTATUS status = func(ThreadHandle, DesiredAccess, ObjectAttributes, ProcessHandle, 
                           StartRoutine, Argument, CreateFlags, ZeroBits, 
                           StackSize, MaximumStackSize, AttributeList);

    VirtualFree(stub, 0, MEM_RELEASE);
    return status;
}

NTSTATUS syscall_NtQuerySystemInformation(
    ULONG SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength,
    PULONG ReturnLength
) {
    uint32_t syscall_num = syscall_resolve_number("NtQuerySystemInformation");
    if (syscall_num == 0) return 0xC0000001;

    void* stub = VirtualAlloc(NULL, sizeof(syscall_stub_template), 
                              MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!stub) return 0xC0000001;

    memcpy(stub, syscall_stub_template, sizeof(syscall_stub_template));
    *(uint32_t*)((unsigned char*)stub + 4) = syscall_num;

    typedef NTSTATUS (*SyscallFunc)(ULONG, PVOID, ULONG, PULONG);
    SyscallFunc func = (SyscallFunc)stub;
    
    NTSTATUS status = func(SystemInformationClass, SystemInformation, SystemInformationLength, ReturnLength);

    VirtualFree(stub, 0, MEM_RELEASE);
    return status;
}

#endif // _WIN32
