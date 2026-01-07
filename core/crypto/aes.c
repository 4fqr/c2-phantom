/**
 * AES-256-GCM Implementation with Hardware Acceleration
 * Uses OpenSSL for performance and security
 */

#include "aes.h"
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <string.h>
#include <cpuid.h>

// Secure memory wipe
static void secure_zero(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) *p++ = 0;
}

int aes_has_hardware_acceleration(void) {
    #ifdef __x86_64__
    unsigned int eax, ebx, ecx, edx;
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
        // Check for AES-NI (bit 25 of ECX)
        return (ecx & (1 << 25)) != 0;
    }
    #endif
    return 0;
}

int aes_gcm_init(aes_gcm_ctx_t *ctx, const uint8_t *key, const uint8_t *iv) {
    if (!ctx || !key || !iv) return -1;

    // Copy key and IV
    memcpy(ctx->key, key, AES_256_KEY_SIZE);
    memcpy(ctx->iv, iv, GCM_IV_SIZE);

    // Create OpenSSL context
    EVP_CIPHER_CTX *evp_ctx = EVP_CIPHER_CTX_new();
    if (!evp_ctx) return -1;

    ctx->internal = evp_ctx;
    return 0;
}

int aes_gcm_encrypt(aes_gcm_ctx_t *ctx,
                    const uint8_t *plaintext, size_t plaintext_len,
                    const uint8_t *aad, size_t aad_len,
                    uint8_t *ciphertext, uint8_t *tag) {
    if (!ctx || !plaintext || !ciphertext || !tag) return -1;

    EVP_CIPHER_CTX *evp_ctx = (EVP_CIPHER_CTX *)ctx->internal;
    int len, ciphertext_len;

    // Initialize encryption
    if (EVP_EncryptInit_ex(evp_ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) {
        return -1;
    }

    // Set IV length
    if (EVP_CIPHER_CTX_ctrl(evp_ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) != 1) {
        return -1;
    }

    // Set key and IV
    if (EVP_EncryptInit_ex(evp_ctx, NULL, NULL, ctx->key, ctx->iv) != 1) {
        return -1;
    }

    // Provide AAD if present
    if (aad && aad_len > 0) {
        if (EVP_EncryptUpdate(evp_ctx, NULL, &len, aad, aad_len) != 1) {
            return -1;
        }
    }

    // Encrypt plaintext
    if (EVP_EncryptUpdate(evp_ctx, ciphertext, &len, plaintext, plaintext_len) != 1) {
        return -1;
    }
    ciphertext_len = len;

    // Finalize encryption
    if (EVP_EncryptFinal_ex(evp_ctx, ciphertext + len, &len) != 1) {
        return -1;
    }
    ciphertext_len += len;

    // Get authentication tag
    if (EVP_CIPHER_CTX_ctrl(evp_ctx, EVP_CTRL_GCM_GET_TAG, GCM_TAG_SIZE, tag) != 1) {
        return -1;
    }

    return ciphertext_len;
}

int aes_gcm_decrypt(aes_gcm_ctx_t *ctx,
                    const uint8_t *ciphertext, size_t ciphertext_len,
                    const uint8_t *aad, size_t aad_len,
                    const uint8_t *tag,
                    uint8_t *plaintext) {
    if (!ctx || !ciphertext || !tag || !plaintext) return -1;

    EVP_CIPHER_CTX *evp_ctx = (EVP_CIPHER_CTX *)ctx->internal;
    int len, plaintext_len;

    // Initialize decryption
    if (EVP_DecryptInit_ex(evp_ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) {
        return -1;
    }

    // Set IV length
    if (EVP_CIPHER_CTX_ctrl(evp_ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) != 1) {
        return -1;
    }

    // Set key and IV
    if (EVP_DecryptInit_ex(evp_ctx, NULL, NULL, ctx->key, ctx->iv) != 1) {
        return -1;
    }

    // Provide AAD if present
    if (aad && aad_len > 0) {
        if (EVP_DecryptUpdate(evp_ctx, NULL, &len, aad, aad_len) != 1) {
            return -1;
        }
    }

    // Decrypt ciphertext
    if (EVP_DecryptUpdate(evp_ctx, plaintext, &len, ciphertext, ciphertext_len) != 1) {
        return -1;
    }
    plaintext_len = len;

    // Set expected tag
    if (EVP_CIPHER_CTX_ctrl(evp_ctx, EVP_CTRL_GCM_SET_TAG, GCM_TAG_SIZE, (void *)tag) != 1) {
        return -1;
    }

    // Finalize and verify authentication
    int ret = EVP_DecryptFinal_ex(evp_ctx, plaintext + len, &len);
    if (ret > 0) {
        plaintext_len += len;
        return plaintext_len;
    } else {
        // Authentication failed - wipe plaintext
        secure_zero(plaintext, plaintext_len);
        return -1;
    }
}

void aes_gcm_cleanup(aes_gcm_ctx_t *ctx) {
    if (!ctx) return;

    // Securely wipe key material
    secure_zero(ctx->key, AES_256_KEY_SIZE);
    secure_zero(ctx->iv, GCM_IV_SIZE);

    // Free OpenSSL context
    if (ctx->internal) {
        EVP_CIPHER_CTX_free((EVP_CIPHER_CTX *)ctx->internal);
        ctx->internal = NULL;
    }
}
