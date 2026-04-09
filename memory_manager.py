import logging

# Configure basic logging for the OS simulation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - MEMORY: %(message)s')

class MemoryManager:
    """
    Memory Management & Failure Scenario Subsystem.
    Authors: Group 3 (Collaboratively developed on all sections)
    
    Handles paging, address translation, and memory exhaustion recovery.
    """
    def __init__(self, total_memory_kb=1024, page_size_kb=64):
        self.page_size = page_size_kb
        self.total_frames = total_memory_kb // page_size_kb
        # Representing physical memory frames; True means free, False means occupied
        self.frames = {i: True for i in range(self.total_frames)} 
        
        # Maps PID to its Page Table. Page Table maps Logical Page Number -> Physical Frame Number
        self.process_page_tables = {} 
        
        # Link to the Scheduler (to be injected during integration)
        self.scheduler = None 

    def register_scheduler(self, scheduler_instance):
        """Allows integration glue to connect the memory manager to Safiye's scheduler."""
        self.scheduler = scheduler_instance

    def allocate_process(self, pid, required_pages):
        """Allocates memory for a new process if available."""
        available_frames = [f for f, is_free in self.frames.items() if is_free]
        
        if len(available_frames) < required_pages:
            logging.warning(f"Memory exhaustion detected trying to allocate {required_pages} pages for PID {pid}.")
            self._handle_memory_exhaustion()
            
            # Retry allocation after attempting recovery
            available_frames = [f for f, is_free in self.frames.items() if is_free]
            if len(available_frames) < required_pages:
                logging.error("System Failure: Unable to recover enough memory.")
                return False

        # Allocate frames
        self.process_page_tables[pid] = {}
        for i in range(required_pages):
            frame = available_frames[i]
            self.frames[frame] = False
            self.process_page_tables[pid][i] = frame
            
        logging.info(f"Allocated {required_pages} pages for PID {pid}.")
        return True

    def translate_address(self, pid, logical_page):
        """Simulates address translation and detects page faults."""
        if pid not in self.process_page_tables:
            logging.error(f"Process {pid} does not exist in memory.")
            return None

        page_table = self.process_page_tables[pid]
        
        if logical_page not in page_table:
            logging.warning(f"PAGE FAULT: PID {pid} attempted to access unmapped page {logical_page}.")
            self._handle_page_fault(pid, logical_page)
            return None
            
        frame_number = page_table[logical_page]
        return frame_number * self.page_size # Returns physical address base

    def deallocate_process(self, pid):
        """Frees all memory associated with a terminated process."""
        if pid in self.process_page_tables:
            for logical_page, frame in self.process_page_tables[pid].items():
                self.frames[frame] = True # Mark frame as free
            del self.process_page_tables[pid]
            logging.info(f"Deallocated all memory for PID {pid}.")

    def _handle_page_fault(self, pid, logical_page):
        """
        Suspends the process by notifying the scheduler.
        """
        logging.info(f"Handling page fault for PID {pid}...")
        if self.scheduler:
            self.scheduler.suspend_process(pid)
            logging.info(f"Notified scheduler to suspend PID {pid} and pick next.")
        else:
            logging.debug("Scheduler not connected. Cannot suspend process.")

    def _handle_memory_exhaustion(self):
        """
        The core failure scenario challenge: Kills the lowest priority process to free memory.
        """
        logging.critical("Initiating memory exhaustion recovery...")
        if self.scheduler:
            lowest_priority_pid = self.scheduler.get_lowest_priority_process()
            if lowest_priority_pid:
                logging.critical(f"Killing lowest priority process (PID {lowest_priority_pid}) to recover memory.")
                self.scheduler.kill_process(lowest_priority_pid)
                self.deallocate_process(lowest_priority_pid)
                logging.info("Memory recovered successfully.")
            else:
                logging.error("No active processes available to kill.")
        else:
            logging.debug("Scheduler not connected. Cannot execute exhaustion recovery.")


# Quick local test to ensure it runs independently before GitHub push
if __name__ == "__main__":
    print("--- Testing Memory Manager Standalone ---")
    mem = MemoryManager(total_memory_kb=256, page_size_kb=64) # 4 frames available
    mem.allocate_process(pid=1, required_pages=2)
    mem.allocate_process(pid=2, required_pages=3) # Should trigger exhaustion warning
    mem.translate_address(pid=1, logical_page=5)  # Should trigger page fault 