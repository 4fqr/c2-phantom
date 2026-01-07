#include "sandbox.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#include <winternl.h>
#else
#include <unistd.h>
#include <sys/sysinfo.h>
#include <sys/statvfs.h>
#endif

int sandbox_check_all(void) {
    int score = 0;
    
    // Run all checks and accumulate score
    if (sandbox_check_timing()) score++;
    if (sandbox_check_artifacts()) score++;
    if (sandbox_check_memory()) score++;
    if (sandbox_check_cpu()) score++;
    if (sandbox_check_disk()) score++;
    if (sandbox_check_processes()) score++;
    
    #ifdef _WIN32
    if (sandbox_check_registry()) score++;
    #endif
    
    // Threshold: 3+ detections = likely sandbox
    return (score >= 3) ? 1 : 0;
}

int sandbox_check_timing(void) {
    #ifdef _WIN32
    // RDTSC timing check
    uint64_t start, end;
    
    start = __rdtsc();
    Sleep(500); // Sleep for 500ms
    end = __rdtsc();
    
    // Calculate CPU cycles
    uint64_t cycles = end - start;
    
    // If less than expected cycles, we're in a sandbox (time acceleration)
    // Typical: ~1-2 billion cycles for 500ms on modern CPUs
    if (cycles < 500000000) {
        return 1; // Sandbox detected
    }
    #else
    // Linux timing check
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    sleep(1);
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    long elapsed = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
    if (elapsed < 900) return 1; // Less than 900ms for 1s sleep = sandbox
    #endif
    
    return 0;
}

int sandbox_check_artifacts(void) {
    #ifdef _WIN32
    // Check for VMware, VirtualBox, QEMU artifacts
    const char* vm_files[] = {
        "C:\\Windows\\System32\\drivers\\vmmouse.sys",
        "C:\\Windows\\System32\\drivers\\vmhgfs.sys",
        "C:\\Windows\\System32\\drivers\\VBoxMouse.sys",
        "C:\\Windows\\System32\\drivers\\VBoxGuest.sys",
        "C:\\Windows\\System32\\drivers\\VBoxSF.sys",
        "C:\\Windows\\System32\\drivers\\qemupci.sys",
        NULL
    };
    
    for (int i = 0; vm_files[i] != NULL; i++) {
        DWORD attrs = GetFileAttributesA(vm_files[i]);
        if (attrs != INVALID_FILE_ATTRIBUTES) {
            return 1; // VM file found
        }
    }
    
    // Check for VMware registry keys
    HKEY key;
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, "SOFTWARE\\VMware, Inc.\\VMware Tools", 0, KEY_READ, &key) == ERROR_SUCCESS) {
        RegCloseKey(key);
        return 1;
    }
    
    // Check for VirtualBox
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, "SOFTWARE\\Oracle\\VirtualBox Guest Additions", 0, KEY_READ, &key) == ERROR_SUCCESS) {
        RegCloseKey(key);
        return 1;
    }
    #endif
    
    return 0;
}

int sandbox_check_user_interaction(void) {
    #ifdef _WIN32
    // Check mouse movement
    POINT cursor1, cursor2;
    GetCursorPos(&cursor1);
    Sleep(5000); // Wait 5 seconds
    GetCursorPos(&cursor2);
    
    // If mouse hasn't moved, likely sandbox
    if (cursor1.x == cursor2.x && cursor1.y == cursor2.y) {
        return 1;
    }
    
    // Check for clicks
    LASTINPUTINFO lii;
    lii.cbSize = sizeof(LASTINPUTINFO);
    GetLastInputInfo(&lii);
    
    // If no input for >30 seconds, suspicious
    DWORD idle_time = (GetTickCount() - lii.dwTime) / 1000;
    if (idle_time > 30) {
        return 1;
    }
    #endif
    
    return 0;
}

int sandbox_check_memory(void) {
    #ifdef _WIN32
    MEMORYSTATUSEX mem;
    mem.dwLength = sizeof(mem);
    GlobalMemoryStatusEx(&mem);
    
    // Less than 2GB RAM = likely VM/sandbox
    uint64_t total_mb = mem.ullTotalPhys / (1024 * 1024);
    if (total_mb < 2048) {
        return 1;
    }
    #else
    struct sysinfo si;
    sysinfo(&si);
    
    uint64_t total_mb = si.totalram / (1024 * 1024);
    if (total_mb < 2048) {
        return 1;
    }
    #endif
    
    return 0;
}

int sandbox_check_cpu(void) {
    #ifdef _WIN32
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    
    // Less than 2 CPUs = likely sandbox
    if (si.dwNumberOfProcessors < 2) {
        return 1;
    }
    #else
    int cpus = sysconf(_SC_NPROCESSORS_ONLN);
    if (cpus < 2) {
        return 1;
    }
    #endif
    
    return 0;
}

int sandbox_check_disk(void) {
    #ifdef _WIN32
    ULARGE_INTEGER total_bytes;
    if (GetDiskFreeSpaceExA("C:\\", NULL, &total_bytes, NULL)) {
        uint64_t total_gb = total_bytes.QuadPart / (1024 * 1024 * 1024);
        
        // Less than 60GB disk = likely sandbox
        if (total_gb < 60) {
            return 1;
        }
    }
    #else
    struct statvfs stat;
    if (statvfs("/", &stat) == 0) {
        uint64_t total_gb = (stat.f_blocks * stat.f_frsize) / (1024 * 1024 * 1024);
        if (total_gb < 60) {
            return 1;
        }
    }
    #endif
    
    return 0;
}

int sandbox_check_network(void) {
    #ifdef _WIN32
    // Check for typical sandbox MAC addresses
    unsigned char sandbox_macs[][3] = {
        {0x00, 0x05, 0x69}, // VMware
        {0x00, 0x0C, 0x29}, // VMware
        {0x00, 0x1C, 0x14}, // VMware
        {0x00, 0x50, 0x56}, // VMware
        {0x08, 0x00, 0x27}, // VirtualBox
        {0x00, 0x00, 0x00}, // Sentinel
    };
    
    // Would need to implement GetAdaptersInfo check here
    // Simplified for now
    #endif
    
    return 0;
}

int sandbox_check_processes(void) {
    #ifdef _WIN32
    // Check for sandbox/analysis tool processes
    const char* sandbox_procs[] = {
        "vmtoolsd.exe",
        "vmwaretray.exe",
        "vmwareuser.exe",
        "vboxservice.exe",
        "vboxtray.exe",
        "procmon.exe",
        "wireshark.exe",
        "fiddler.exe",
        "ollydbg.exe",
        "x64dbg.exe",
        "ida.exe",
        "ida64.exe",
        NULL
    };
    
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE) return 0;
    
    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(pe);
    
    if (Process32First(snap, &pe)) {
        do {
            for (int i = 0; sandbox_procs[i] != NULL; i++) {
                if (_stricmp(pe.szExeFile, sandbox_procs[i]) == 0) {
                    CloseHandle(snap);
                    return 1; // Sandbox process found
                }
            }
        } while (Process32Next(snap, &pe));
    }
    
    CloseHandle(snap);
    #endif
    
    return 0;
}

int sandbox_check_registry(void) {
    #ifdef _WIN32
    // Check for sandbox registry artifacts
    const char* sandbox_keys[] = {
        "SOFTWARE\\VMware, Inc.\\VMware Tools",
        "SOFTWARE\\Oracle\\VirtualBox Guest Additions",
        "HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 0\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0", // Check for VBOX, QEMU, VMWARE in Identifier
        NULL
    };
    
    HKEY key;
    for (int i = 0; sandbox_keys[i] != NULL; i++) {
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, sandbox_keys[i], 0, KEY_READ, &key) == ERROR_SUCCESS) {
            RegCloseKey(key);
            return 1;
        }
    }
    #endif
    
    return 0;
}

int sandbox_check_files(void) {
    #ifdef _WIN32
    // Check for sandbox analysis files
    const char* sandbox_files[] = {
        "C:\\analysis",
        "C:\\sandbox",
        "C:\\cwsandbox",
        "C:\\sample",
        "C:\\malware",
        NULL
    };
    
    for (int i = 0; sandbox_files[i] != NULL; i++) {
        DWORD attrs = GetFileAttributesA(sandbox_files[i]);
        if (attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_DIRECTORY)) {
            return 1;
        }
    }
    #endif
    
    return 0;
}

void sandbox_delay_execution(uint32_t seconds) {
    #ifdef _WIN32
    Sleep(seconds * 1000);
    #else
    sleep(seconds);
    #endif
}

void sandbox_sleep_with_checks(uint32_t seconds) {
    // Sleep in intervals while checking for time acceleration
    uint32_t intervals = seconds / 5;
    
    for (uint32_t i = 0; i < intervals; i++) {
        clock_t start = clock();
        sandbox_delay_execution(5);
        clock_t end = clock();
        
        double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
        
        // If time moved too fast, exit
        if (elapsed < 4.0) {
            exit(0);
        }
    }
}
