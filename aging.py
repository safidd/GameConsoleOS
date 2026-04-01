from pcb import PCB, ProcessState
from collections import deque

class AgingScheduler:
    def __init__(self, time_quantum=2, aging_threshold=4):
        self.ready_queue = deque()
        self.time_quantum = time_quantum
        self.aging_threshold = aging_threshold  # boost priority after this many waits
        self.wait_time = {}   # pid -> how long waiting
        self.current_time = 0

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        self.wait_time[process.pid] = 0
        print(f"[Scheduler] {process.name} added (priority {process.priority})")

    def age_processes(self, running_pid):
        for p in self.ready_queue:
            if p.pid == running_pid:
                continue
            self.wait_time[p.pid] += self.time_quantum
            if self.wait_time[p.pid] >= self.aging_threshold:
                old_priority = p.priority
                p.priority += 1
                self.wait_time[p.pid] = 0
                print(f"[Aging] {p.name} waited too long — priority boosted {old_priority} -> {p.priority}")

    def run(self):
        print(f"\n[Scheduler] Starting Aging Scheduler (quantum={self.time_quantum}, threshold={self.aging_threshold})...\n")
        while self.ready_queue:
            # always pick highest priority process
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p.priority, reverse=True))
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING

            ticks = min(self.time_quantum, process.burst_time - process.cpu_time)
            process.cpu_time += ticks
            self.current_time += ticks
            print(f"[t={self.current_time}] Running: {process.name} (priority {process.priority}) | CPU: {process.cpu_time}/{process.burst_time}")

            # age all waiting processes
            self.age_processes(process.pid)

            if process.cpu_time >= process.burst_time:
                process.state = ProcessState.TERMINATED
                print(f"[Scheduler] Terminated: {process.name}\n")
            else:
                process.state = ProcessState.READY
                self.ready_queue.append(process)

        print(f"[Scheduler] All processes finished at t={self.current_time}")

if __name__ == "__main__":
    print("=" * 55)
    print("     AGING MECHANISM DEMO")
    print("=" * 55)

    print("\n--- WITHOUT Aging (low priority may starve) ---\n")
    from scheduler import FIFOScheduler
    fifo = FIFOScheduler()
    p1 = PCB(pid=1, name="GameProcess",    priority=3, memory_required=256)
    p2 = PCB(pid=2, name="AudioEngine",    priority=3, memory_required=60)
    p3 = PCB(pid=3, name="DownloadMgr",    priority=1, memory_required=80)
    p1.burst_time = 6
    p2.burst_time = 4
    p3.burst_time = 2
    fifo.add_process(p1)
    fifo.add_process(p2)
    fifo.add_process(p3)
    fifo.run()

    print("\n--- WITH Aging (low priority gets boosted) ---\n")
    scheduler = AgingScheduler(time_quantum=2, aging_threshold=4)
    q1 = PCB(pid=1, name="GameProcess",    priority=3, memory_required=256)
    q2 = PCB(pid=2, name="AudioEngine",    priority=3, memory_required=60)
    q3 = PCB(pid=3, name="DownloadMgr",    priority=1, memory_required=80)
    q1.burst_time = 6
    q2.burst_time = 4
    q3.burst_time = 2
    scheduler.add_process(q1)
    scheduler.add_process(q2)
    scheduler.add_process(q3)
    scheduler.run()

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("Without aging: DownloadMgr waits until both high")
    print("priority processes finish — potential starvation.")
    print("With aging: DownloadMgr gets priority boost after")
    print("waiting too long and gets CPU time sooner.")
    print("=" * 55)