#ifndef ANTI_SANDBOX_H
#define ANTI_SANDBOX_H

#include <stdint.h>

// Sandbox detection techniques
int sandbox_check_all(void);

// Individual checks
int sandbox_check_timing(void);       // Timing-based detection
int sandbox_check_artifacts(void);    // VM/sandbox artifacts
int sandbox_check_user_interaction(void);  // Mouse/keyboard simulation
int sandbox_check_memory(void);       // Memory size checks
int sandbox_check_cpu(void);          // CPU count checks
int sandbox_check_disk(void);         // Disk size checks
int sandbox_check_network(void);      // Network configuration
int sandbox_check_processes(void);    // Sandbox process detection
int sandbox_check_registry(void);     // Registry artifact detection (Windows)
int sandbox_check_files(void);        // File system artifacts

// Evasion actions
void sandbox_delay_execution(uint32_t seconds);
void sandbox_sleep_with_checks(uint32_t seconds);

#endif // ANTI_SANDBOX_H
