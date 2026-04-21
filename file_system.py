import time
from pcb import ProcessState
class File:
    def __init__(self, name, data=""):
        self.name = name
        self.data = data
        self.is_locked = False
        self.size = len(data)

class FileSystem:
    def __init__(self):
        self.disk = {
            "/system": {},
            "/games": {},
            "/saves": {}
        }
    
    def create_file(self, path, filename, data=""):
        if path not in self.disk:
            print(f"[File System Error] Cannot create. Directory '{path}' does not exist.")
            return False
        
        if filename in self.disk[path]:
            print(f"[File System Error] File '{filename}' already exists in '{path}'.")
            return False
        
        new_file = File(name=filename, data=data)
        self.disk[path][filename] = new_file
        print(f"[File System] Created '{filename}' at '{path}'.")
        return True

    def read_file(self, path, filename):
        if path not in self.disk:
            print(f"[File System Error] Cannot read. Directory '{path}' does not exist.")
            return None
            
        if filename not in self.disk[path]:
            print(f"[File System Error] File '{filename}' not found in '{path}'.")
            return None
            
        target_file = self.disk[path][filename]
        
        if target_file.is_locked:
            print(f"[Concurrency Block] Cannot read '{filename}'. File is currently locked!")
            return None
        
        print(f"[File System] Read '{filename}' successfully. Size: {target_file.size} bytes.")
        return target_file.data

    def write_file(self, path, filename, new_data, process=None):
        if path not in self.disk:
            print(f"[File System Error] Cannot write. Directory '{path}' does not exist.")
            return False
            
        if filename not in self.disk[path]:
            print(f"[File System Error] File '{filename}' not found in '{path}'.")
            return False
            
        target_file = self.disk[path][filename]
        
        if target_file.is_locked:
            print(f"[Concurrency Block] Cannot write to '{filename}'. File is currently locked!")
            return False
            
        target_file.is_locked = True
        print(f"[File System] Acquired lock. Writing to '{filename}'...")
        
        # --- WEEK 3 CROSS-COMPONENT INTEGRATION ---
        if process:
            process.state = ProcessState.BLOCKED
            print(f"[OS] Process {process.pid} is BLOCKED waiting for File I/O.")
            
            # Simulate the slow hardware I/O
            time.sleep(1) 
            
        target_file.data = new_data
        target_file.size = len(new_data)
        
        target_file.is_locked = False
        print(f"[File System] Write complete and lock released. New size: {target_file.size} bytes.")
        
        # Wake the process back up
        if process:
            process.state = ProcessState.READY
            print(f"[OS] I/O complete. Process {process.pid} is READY.")
            
        return True

    def delete_file(self, path, filename):
        if path not in self.disk:
            print(f"[File System Error] Cannot delete. Directory '{path}' does not exist.")
            return False
            
        if filename not in self.disk[path]:
            print(f"[File System Error] File '{filename}' not found in '{path}'.")
            return False
            
        target_file = self.disk[path][filename]
        
        if target_file.is_locked:
            print(f"[System Error] Cannot delete '{filename}'. It is currently in use (Locked)!")
            return False
            
        del self.disk[path][filename]
        print(f"[File System] File '{filename}' successfully deleted from '{path}'.")
        return True