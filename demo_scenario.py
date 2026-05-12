import logging
from memory_manager import MemoryManager

# Configure logging for the live demo
logging.basicConfig(level=logging.INFO, format='%(message)s')

class MockScheduler:
    """A minimal mock scheduler to test the memory manager's failure recovery."""
    def __init__(self):
        # Format: {pid: priority} - Lower number = higher priority
        self.active_processes = {
            1: 1, # High priority (e.g., Core Game Loop)
            2: 2, # Medium priority (e.g., Save Thread)
            3: 5  # Low priority (e.g., Background Download)
        }
    
    def suspend_process(self, pid):
        print(f"[SCHEDULER] Suspending PID {pid} due to Page Fault.")

    def get_lowest_priority_process(self):
        if not self.active_processes:
            return None
        # Find the PID with the highest priority number (lowest actual priority)
        lowest_pid = max(self.active_processes, key=self.active_processes.get)
        return lowest_pid

    def kill_process(self, pid):
        print(f"[SCHEDULER] Terminating PID {pid} to free up system resources.")
        if pid in self.active_processes:
            del self.active_processes[pid]

def run_demo():
    print("=== STARTING GAME CONSOLE OS DEMO ===")
    
    # Initialize Memory Manager with very limited memory (4 frames total)
    mem = MemoryManager(total_memory_kb=256, page_size_kb=64)
    scheduler = MockScheduler()
    mem.register_scheduler(scheduler)

    print("\n[SCENARIO] Booting Core Game and Save Threads...")
    mem.allocate_process(pid=1, required_pages=2) # Uses 2 frames
    mem.allocate_process(pid=2, required_pages=1) # Uses 1 frame
    
    print("\n[SCENARIO] User initiates a massive background download...")
    # This requires 3 frames, but only 1 is left! This will trigger the failure scenario.
    mem.allocate_process(pid=3, required_pages=3) 

    print("\n[SCENARIO] Simulating Game Loop Memory Access...")
    # Translate address for PID 1 to prove system is still stable
    physical_addr = mem.translate_address(pid=1, logical_page=1)
    print(f"[SYSTEM] PID 1 logical page 1 resolved to physical address base: {physical_addr}")

    print("\n=== DEMO COMPLETE ===")

if __name__ == "__main__":
    run_demo() 