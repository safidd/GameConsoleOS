from pcb import ProcessState

class MemoryManager:
    def __init__(self, total_memory=1024):
        self.total_memory = total_memory
        self.available_memory = total_memory
        self.memory_map = {}

    def allocate(self, process):
        if process.memory_required > self.available_memory:
            print(f"[Memory] ERROR: Not enough memory for {process.name}!")
            print(f"[Memory] Required: {process.memory_required}MB | Available: {self.available_memory}MB")
            return False
        self.memory_map[process.pid] = process.memory_required
        self.available_memory -= process.memory_required
        print(f"[Memory] Allocated {process.memory_required}MB to {process.name} (PID:{process.pid}) | Remaining: {self.available_memory}MB")
        return True

    def deallocate(self, process):
        if process.pid in self.memory_map:
            freed = self.memory_map.pop(process.pid)
            self.available_memory += freed
            print(f"[Memory] Freed {freed}MB from {process.name} (PID:{process.pid}) | Available: {self.available_memory}MB")

    def handle_exhaustion(self, process, processes):
        print(f"\n[Memory] MEMORY EXHAUSTION -- need {process.memory_required}MB, only {self.available_memory}MB free!")
        candidates = [p for p in processes if p.pid in self.memory_map and p.pid != process.pid]
        while self.available_memory < process.memory_required and candidates:
            victim = min(candidates, key=lambda p: p.priority)
            victim.state = ProcessState.TERMINATED
            self.deallocate(victim)
            candidates.remove(victim)
            print(f"[Memory] Killed {victim.name} (PID:{victim.pid}) -- lowest priority")
            print(f"[Memory] Available memory now: {self.available_memory}MB\n")

    def status(self):
        print(f"\n[Memory] Total: {self.total_memory}MB | Used: {self.total_memory - self.available_memory}MB | Free: {self.available_memory}MB")
        for pid, mem in self.memory_map.items():
            print(f"  PID:{pid} -> {mem}MB")