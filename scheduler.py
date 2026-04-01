from pcb import PCB, ProcessState
from collections import deque

class FIFOScheduler:
    def __init__(self):
        self.ready_queue = deque()

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        print(f"[Scheduler] Process {process.name} (PID:{process.pid}) added to ready queue")

    def run(self):
        print("\n[Scheduler] Starting FIFO Scheduler...\n")
        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING
            print(f"[Scheduler] Running: {process}")
            process.cpu_time += 1
            process.state = ProcessState.TERMINATED
            print(f"[Scheduler] Terminated: {process.name} (PID:{process.pid})\n")
        print("[Scheduler] All processes finished.")

# Test
if __name__ == "__main__":
    scheduler = FIFOScheduler()

    scheduler.add_process(PCB(pid=1, name="GameProcess", priority=3, memory_required=512))
    scheduler.add_process(PCB(pid=2, name="DownloadManager", priority=1, memory_required=128))
    scheduler.add_process(PCB(pid=3, name="SaveThread", priority=2, memory_required=64))

    scheduler.run()