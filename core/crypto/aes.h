/**
 * AES-256-GCM Implementation with Hardware Acceleration
 * 
 * Features:
 * - AES-NI hardware acceleration (Intel/AMD CPUs)
 * - GCM mode for authenticated encryption
 * - Zero-copy operations
 * - Constant-time implementation (timing attack resistant)
 */

#ifndef C2_CRYPTO_AES_H
#define C2_CRYPTO_AES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// AES-256 key size
#define AES_256_KEY_SIZE 32
#define AES_BLOCK_SIZE 16
#define GCM_IV_SIZE 12
#define GCM_TAG_SIZE 16

/**
 * AES-256-GCM context structure
 */
typedef struct {
    uint8_t key[AES_256_KEY_SIZE];
    uint8_t iv[GCM_IV_SIZE];
    void *internal;  // OpenSSL EVP_CIPHER_CTX
} aes_gcm_ctx_t;

/**
 * Initialize AES-256-GCM context
 * 
 * @param ctx Context to initialize
 * @param key 32-byte encryption key
 * @param iv 12-byte initialization vector
 * @return 0 on success, -1 on error
 */
int aes_gcm_init(aes_gcm_ctx_t *ctx, const uint8_t *key, const uint8_t *iv);

/**
 * Encrypt data with AES-256-GCM
 * 
 * @param ctx Initialized context
 * @param plaintext Input plaintext
 * @param plaintext_len Length of plaintext
 * @param aad Additional authenticated data (can be NULL)
 * @param aad_len Length of AAD
 * @param ciphertext Output buffer (must be >= plaintext_len)
 * @param tag Output authentication tag (16 bytes)
 * @return Number of bytes encrypted, -1 on error
 */
int aes_gcm_encrypt(aes_gcm_ctx_t *ctx,
                    const uint8_t *plaintext, size_t plaintext_len,
                    const uint8_t *aad, size_t aad_len,
                    uint8_t *ciphertext, uint8_t *tag);

/**
 * Decrypt data with AES-256-GCM
 * 
 * @param ctx Initialized context
 * @param ciphertext Input ciphertext
 * @param ciphertext_len Length of ciphertext
 * @param aad Additional authenticated data (must match encryption)
 * @param aad_len Length of AAD
 * @param tag Authentication tag to verify (16 bytes)
 * @param plaintext Output buffer (must be >= ciphertext_len)
 * @return Number of bytes decrypted, -1 on error or auth failure
 */
int aes_gcm_decrypt(aes_gcm_ctx_t *ctx,
                    const uint8_t *ciphertext, size_t ciphertext_len,
                    const uint8_t *aad, size_t aad_len,
                    const uint8_t *tag,
                    uint8_t *plaintext);

/**
 * Clean up AES-256-GCM context
 * Securely wipes sensitive data from memory
 * 
 * @param ctx Context to clean up
 */
void aes_gcm_cleanup(aes_gcm_ctx_t *ctx);

/**
 * Check if AES-NI hardware acceleration is available
 * 
 * @return 1 if available, 0 otherwise
 */
int aes_has_hardware_acceleration(void);

#ifdef __cplusplus
}
#endif

#endif // C2_CRYPTO_AES_H
