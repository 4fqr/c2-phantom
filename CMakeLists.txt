cmake_minimum_required(VERSION 3.15)
project(C2Phantom C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Build options
option(ENABLE_HARDWARE_ACCEL "Enable hardware acceleration (AES-NI)" ON)
option(BUILD_STATIC "Build static libraries" ON)
option(ENABLE_OBFUSCATION "Enable code obfuscation" OFF)

# Compiler flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -march=native -ffunction-sections -fdata-sections")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -ffunction-sections -fdata-sections")
    
    if(ENABLE_OBFUSCATION)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-inline -fno-unroll-loops")
    endif()
    
    # Strip symbols
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--gc-sections -s")
endif()

# Find OpenSSL
find_package(OpenSSL REQUIRED)
include_directories(${OPENSSL_INCLUDE_DIR})

# Core crypto library
add_library(c2_crypto STATIC
    core/crypto/aes.c
    core/crypto/aes.h
)
target_link_libraries(c2_crypto ${OPENSSL_LIBRARIES})
target_include_directories(c2_crypto PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/crypto)

# Core network library
add_library(c2_network STATIC
    core/network/beacon.c
    core/network/beacon.h
)
target_link_libraries(c2_network c2_crypto)
target_include_directories(c2_network PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/network)

# Core process library
add_library(c2_process STATIC
    core/process/inject.c
    core/process/inject.h
)
target_include_directories(c2_process PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/process)

# Core evasion library - EXPANDED
add_library(c2_evasion STATIC
    core/evasion/amsi.c
    core/evasion/amsi.h
    core/evasion/etw.c
    core/evasion/etw.h
)
target_include_directories(c2_evasion PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/evasion)

# Core syscall library (direct syscalls for EDR bypass)
add_library(c2_syscall STATIC
    core/syscall/direct.c
    core/syscall/direct.h
)
target_include_directories(c2_syscall PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/syscall)

# Core hooking library (inline hooks, API interception)
add_library(c2_hooks STATIC
    core/hooks/inline.c
    core/hooks/inline.h
)
target_include_directories(c2_hooks PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/hooks)

# Core anti-analysis library (sandbox, VM detection)
add_library(c2_anti STATIC
    core/anti/sandbox.c
    core/anti/sandbox.h
)
target_include_directories(c2_anti PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/core/anti)

# Combined core library for Python FFI
add_library(c2core SHARED
    core/crypto/aes.c
    core/network/beacon.c
    core/evasion/amsi.c
    core/evasion/etw.c
    core/process/inject.c
    core/syscall/direct.c
    core/hooks/inline.c
    core/anti/sandbox.c
)
target_link_libraries(c2core ${OPENSSL_LIBRARIES})
target_include_directories(c2core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/core
    ${OPENSSL_INCLUDE_DIR}
)

# Platform-specific libraries
if(WIN32)
    target_link_libraries(c2core 
        ntdll 
        advapi32 
        psapi
        tlhelp32
    )
endif()

# Test executables
add_executable(test_crypto tests/test_crypto.c)
target_link_libraries(test_crypto c2_crypto)

# Install targets
install(TARGETS c2_crypto c2_network c2_process c2_evasion c2_syscall c2_hooks c2_anti c2core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY core/crypto/ DESTINATION include/c2phantom/crypto
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY core/network/ DESTINATION include/c2phantom/network
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY core/process/ DESTINATION include/c2phantom/process
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY core/evasion/ DESTINATION include/c2phantom/evasion
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY core/syscall/ DESTINATION include/c2phantom/syscall
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY core/hooks/ DESTINATION include/c2phantom/hooks
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY core/anti/ DESTINATION include/c2phantom/anti
    FILES_MATCHING PATTERN "*.h"
)
