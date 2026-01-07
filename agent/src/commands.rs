use std::process::Command;
use std::io::{self, Read};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

pub struct CommandExecutor;

impl CommandExecutor {
    pub fn execute_shell(command: &str) -> io::Result<String> {
        #[cfg(target_os = "windows")]
        {
            Self::execute_powershell(command)
        }
        
        #[cfg(target_os = "linux")]
        {
            Self::execute_bash(command)
        }
    }
    
    #[cfg(target_os = "windows")]
    pub fn execute_powershell(command: &str) -> io::Result<String> {
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        
        let output = Command::new("powershell.exe")
            .args(&[
                "-NoProfile",
                "-NonInteractive",
                "-WindowStyle", "Hidden",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                command
            ])
            .creation_flags(CREATE_NO_WINDOW)
            .output()?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        
        if output.status.success() {
            Ok(stdout.to_string())
        } else {
            Ok(format!("Error: {}\n{}", stderr, stdout))
        }
    }
    
    #[cfg(target_os = "windows")]
    pub fn execute_cmd(command: &str) -> io::Result<String> {
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        
        let output = Command::new("cmd.exe")
            .args(&["/c", command])
            .creation_flags(CREATE_NO_WINDOW)
            .output()?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.to_string())
    }
    
    #[cfg(target_os = "linux")]
    pub fn execute_bash(command: &str) -> io::Result<String> {
        let output = Command::new("/bin/sh")
            .args(&["-c", command])
            .output()?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.to_string())
    }
    
    pub fn execute_with_timeout(command: &str, timeout_secs: u64) -> io::Result<String> {
        use std::time::Duration;
        use std::sync::mpsc;
        use std::thread;
        
        let (tx, rx) = mpsc::channel();
        let cmd = command.to_string();
        
        thread::spawn(move || {
            let result = Self::execute_shell(&cmd);
            let _ = tx.send(result);
        });
        
        match rx.recv_timeout(Duration::from_secs(timeout_secs)) {
            Ok(result) => result,
            Err(_) => Err(io::Error::new(io::ErrorKind::TimedOut, "Command timed out"))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_command_execution() {
        let result = CommandExecutor::execute_shell("echo test").unwrap();
        assert!(result.contains("test"));
    }
}
