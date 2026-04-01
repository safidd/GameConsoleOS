import time

class ProcessState:
    NEW        = "NEW"
    READY      = "READY"
    RUNNING    = "RUNNING"
    BLOCKED    = "BLOCKED"
    TERMINATED = "TERMINATED"

class PCB:
    def __init__(self, pid, name, priority, memory_required):
        self.pid = pid
        self.name = name
        self.state = ProcessState.NEW
        self.priority = priority
        self.memory_required = memory_required
        self.open_files = []
        self.created_at = time.time()
        self.cpu_time = 0
        self.is_io_bound = False  # True if this process does file I/O

    def __repr__(self):
        return f"[PCB | PID:{self.pid} | {self.name} | {self.state} | Priority:{self.priority}]"

# Test
if __name__ == "__main__":
    p1 = PCB(pid=1, name="GameProcess", priority=3, memory_required=512)
    p2 = PCB(pid=2, name="DownloadManager", priority=1, memory_required=128)
    p3 = PCB(pid=3, name="SaveThread", priority=2, memory_required=64)

    print(p1)
    print(p2)
    print(p3)