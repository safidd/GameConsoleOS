from pcb import PCB, ProcessState
from collections import deque

class FIFOScheduler:
    def __init__(self):
        self.ready_queue = deque()

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        print(f"[Scheduler] {process.name} (PID:{process.pid}) added | Priority:{process.priority}")

    def run(self):
        print("\n[Scheduler] Starting FIFO — Starvation Demo...\n")
        total_time = 0
        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING
            wait_time = total_time
            print(f"[Scheduler] Running: {process.name} | Waited: {wait_time} units")
            total_time += process.burst_time
            process.cpu_time = process.burst_time
            process.state = ProcessState.TERMINATED
            if wait_time > 5:
                print(f"[Scheduler] WARNING: {process.name} waited {wait_time} units -- STARVATION!")
            print(f"[Scheduler] Terminated: {process.name}\n")
        print(f"[Scheduler] Total time: {total_time} units")

class RoundRobinScheduler:
    def __init__(self, time_quantum=2):
        self.ready_queue = deque()
        self.time_quantum = time_quantum

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        print(f"[Scheduler] {process.name} (PID:{process.pid}) added | Priority:{process.priority}")

    def run(self):
        print(f"\n[Scheduler] Starting Round Robin (quantum={self.time_quantum}) — No Starvation...\n")
        total_time = 0
        arrival_time = {}
        first_run = {}

        for p in list(self.ready_queue):
            arrival_time[p.pid] = 0

        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING

            if process.pid not in first_run:
                first_run[process.pid] = total_time
                wait = first_run[process.pid] - arrival_time[process.pid]
                print(f"[Scheduler] {process.name} first run at time {total_time} | Initial wait: {wait} units")

            if process.cpu_time + self.time_quantum >= process.burst_time:
                remaining = process.burst_time - process.cpu_time
                total_time += remaining
                process.cpu_time = process.burst_time
                process.state = ProcessState.TERMINATED
                print(f"[Scheduler] Terminated: {process.name} at time {total_time}\n")
            else:
                process.cpu_time += self.time_quantum
                total_time += self.time_quantum
                process.state = ProcessState.READY
                self.ready_queue.append(process)

        print(f"[Scheduler] Total time: {total_time} units")

if __name__ == "__main__":
    print("=" * 55)
    print("     STARVATION DEMO — FIFO vs Round Robin")
    print("=" * 55)

    print("\n--- FIFO: High burst process blocks everything ---\n")
    fifo = FIFOScheduler()
    p1 = PCB(pid=1, name="GameProcess",     priority=3, memory_required=256)
    p2 = PCB(pid=2, name="DownloadManager", priority=1, memory_required=128)
    p3 = PCB(pid=3, name="SaveThread",      priority=2, memory_required=64)
    p4 = PCB(pid=4, name="Screenshot",      priority=1, memory_required=64)
    p1.burst_time = 20
    p2.burst_time = 3
    p3.burst_time = 2
    p4.burst_time = 1
    fifo.add_process(p1)
    fifo.add_process(p2)
    fifo.add_process(p3)
    fifo.add_process(p4)
    fifo.run()

    print("\n" + "=" * 55)
    print("\n--- Round Robin: Everyone gets a fair turn ---\n")
    rr = RoundRobinScheduler(time_quantum=2)
    p1 = PCB(pid=1, name="GameProcess",     priority=3, memory_required=256)
    p2 = PCB(pid=2, name="DownloadManager", priority=1, memory_required=128)
    p3 = PCB(pid=3, name="SaveThread",      priority=2, memory_required=64)
    p4 = PCB(pid=4, name="Screenshot",      priority=1, memory_required=64)
    p1.burst_time = 20
    p2.burst_time = 3
    p3.burst_time = 2
    p4.burst_time = 1
    rr.add_process(p1)
    rr.add_process(p2)
    rr.add_process(p3)
    rr.add_process(p4)
    rr.run()

    print("\n" + "=" * 55)
    print("CONCLUSION: FIFO causes starvation for small processes.")
    print("Round Robin gives every process CPU time within 2 units.")
    print("=" * 55)