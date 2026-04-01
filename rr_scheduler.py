from pcb import PCB, ProcessState
from collections import deque

class RoundRobinScheduler:
    def __init__(self, time_quantum=2):
        self.ready_queue = deque()
        self.blocked_queue = []
        self.time_quantum = time_quantum

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        print(f"[Scheduler] {process.name} (PID:{process.pid}) added to ready queue")

    def unblock_all(self):
        for process in list(self.blocked_queue):
            self.blocked_queue.remove(process)
            process.state = ProcessState.READY
            self.ready_queue.append(process)
            print(f"[Scheduler] {process.name} (PID:{process.pid}) UNBLOCKED, back to ready queue")

    def run(self):
        print(f"\n[Scheduler] Starting Round Robin (quantum={self.time_quantum})...\n")
        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING
            print(f"[Scheduler] Running: {process}")

            # Trigger I/O block once per process
            if process.is_io_bound and not process.io_done:
                process.state = ProcessState.BLOCKED
                process.io_done = True
                self.blocked_queue.append(process)
                print(f"[Scheduler] {process.name} BLOCKED due to file I/O\n")
                self.unblock_all()
                continue

            if process.cpu_time + self.time_quantum >= process.burst_time:
                process.cpu_time = process.burst_time
                process.state = ProcessState.TERMINATED
                # free memory when process finishes
                if hasattr(process, 'memory_manager'):
                    process.memory_manager.deallocate(process)
                print(f"[Scheduler] Terminated: {process.name} (PID:{process.pid})\n")
            else:
                process.cpu_time += self.time_quantum
                process.state = ProcessState.READY
                self.ready_queue.append(process)
                print(f"[Scheduler] {process.name} used quantum, back to queue. CPU time: {process.cpu_time}\n")

        print("[Scheduler] All processes finished.")