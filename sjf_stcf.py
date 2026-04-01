from pcb import PCB, ProcessState
from collections import deque

class SJFScheduler:
    """Shortest Job First — non-preemptive, runs shortest burst first"""
    def __init__(self):
        self.processes = []
        self.current_time = 0
        self.stats = {}

    def add_process(self, process):
        self.processes.append(process)
        self.stats[process.pid] = {"wait": 0, "turnaround": 0, "response": -1}
        print(f"[SJF] Added {process.name} (burst={process.burst_time}, arrival={process.arrival_time})")

    def run(self):
        print(f"\n[SJF] Starting Shortest Job First...\n")
        remaining = list(self.processes)

        while remaining:
            # get all processes that have arrived
            available = [p for p in remaining if p.arrival_time <= self.current_time]

            if not available:
                # jump to next arrival
                self.current_time = min(p.arrival_time for p in remaining)
                continue

            # pick shortest burst
            process = min(available, key=lambda p: p.burst_time)
            remaining.remove(process)

            wait = self.current_time - process.arrival_time
            self.stats[process.pid]["wait"] = wait
            self.stats[process.pid]["response"] = wait

            process.state = ProcessState.RUNNING
            print(f"[t={self.current_time}] Running: {process.name} (burst={process.burst_time}) | Waited: {wait} units")
            self.current_time += process.burst_time
            process.cpu_time = process.burst_time
            process.state = ProcessState.TERMINATED

            turnaround = self.current_time - process.arrival_time
            self.stats[process.pid]["turnaround"] = turnaround
            print(f"[t={self.current_time}] Terminated: {process.name} | Turnaround: {turnaround}\n")

        print(f"[SJF] All processes finished at t={self.current_time}")

class STCFScheduler:
    """Shortest Time to Completion First — preemptive SJF"""
    def __init__(self):
        self.processes = []
        self.current_time = 0
        self.stats = {}

    def add_process(self, process):
        self.processes.append(process)
        self.stats[process.pid] = {"wait": 0, "turnaround": 0, "response": -1, "remaining": process.burst_time}
        print(f"[STCF] Added {process.name} (burst={process.burst_time}, arrival={process.arrival_time})")

    def run(self):
        print(f"\n[STCF] Starting Shortest Time to Completion First...\n")
        completed = 0
        n = len(self.processes)
        prev = None

        while completed < n:
            # available processes at current time
            available = [p for p in self.processes
                        if p.arrival_time <= self.current_time
                        and p.state != ProcessState.TERMINATED]

            if not available:
                self.current_time += 1
                continue

            # pick process with shortest remaining time
            process = min(available, key=lambda p: self.stats[p.pid]["remaining"])

            # record first run (response time)
            if self.stats[process.pid]["response"] == -1:
                self.stats[process.pid]["response"] = self.current_time - process.arrival_time

            if prev != process:
                print(f"[t={self.current_time}] Running: {process.name} (remaining={self.stats[process.pid]['remaining']})")

            process.state = ProcessState.RUNNING
            self.stats[process.pid]["remaining"] -= 1
            self.current_time += 1
            prev = process

            if self.stats[process.pid]["remaining"] == 0:
                process.state = ProcessState.TERMINATED
                turnaround = self.current_time - process.arrival_time
                wait = turnaround - process.burst_time
                self.stats[process.pid]["turnaround"] = turnaround
                self.stats[process.pid]["wait"] = wait
                print(f"[t={self.current_time}] Terminated: {process.name} | Turnaround: {turnaround} | Wait: {wait}\n")
                completed += 1
                prev = None

        print(f"[STCF] All processes finished at t={self.current_time}")

def print_comparison(schedulers_stats, processes):
    print("\n" + "=" * 65)
    print("     SCHEDULER COMPARISON — SJF vs STCF")
    print("=" * 65)
    col = 14
    print(f"\n  {'Process':<{col}} {'Arrival':>8} {'Burst':>6} {'SJF Wait':>9} {'SJF TR':>7} {'STCF Wait':>10} {'STCF TR':>8}")
    print(f"  {'-'*col} {'-------':>8} {'-----':>6} {'--------':>9} {'------':>7} {'---------':>10} {'-------':>8}")

    sjf_stats, stcf_stats = schedulers_stats

    total_sjf_wait = total_sjf_tr = total_stcf_wait = total_stcf_tr = 0

    for p in processes:
        sw = sjf_stats[p.pid]["wait"]
        st = sjf_stats[p.pid]["turnaround"]
        cw = stcf_stats[p.pid]["wait"]
        ct = stcf_stats[p.pid]["turnaround"]
        total_sjf_wait += sw; total_sjf_tr += st
        total_stcf_wait += cw; total_stcf_tr += ct
        print(f"  {p.name:<{col}} {p.arrival_time:>8} {p.burst_time:>6} {sw:>9} {st:>7} {cw:>10} {ct:>8}")

    n = len(processes)
    print(f"\n  {'AVERAGE':<{col}} {'':>8} {'':>6} {total_sjf_wait/n:>9.1f} {total_sjf_tr/n:>7.1f} {total_stcf_wait/n:>10.1f} {total_stcf_tr/n:>8.1f}")
    print("=" * 65)

if __name__ == "__main__":
    print("=" * 65)
    print("     SJF vs STCF SCHEDULER DEMO")
    print("=" * 65)

    # processes with different arrival times
    process_data = [
        ("GameProcess",   0, 10),  # arrives at 0, burst 10
        ("AudioEngine",   2, 4),   # arrives at 2, burst 4
        ("DownloadMgr",   4, 2),   # arrives at 4, burst 2
        ("SaveThread",    6, 3),   # arrives at 6, burst 3
    ]

    print("\n--- SJF (Non-preemptive) ---\n")
    sjf = SJFScheduler()
    processes_sjf = []
    for name, arrival, burst in process_data:
        p = PCB(pid=len(processes_sjf)+1, name=name, priority=2, memory_required=64)
        p.burst_time = burst
        p.arrival_time = arrival
        p.cpu_time = 0
        processes_sjf.append(p)
        sjf.add_process(p)
    sjf.run()

    print("\n--- STCF (Preemptive SJF) ---\n")
    stcf = STCFScheduler()
    processes_stcf = []
    for name, arrival, burst in process_data:
        p = PCB(pid=len(processes_stcf)+1, name=name, priority=2, memory_required=64)
        p.burst_time = burst
        p.arrival_time = arrival
        p.cpu_time = 0
        processes_stcf.append(p)
        stcf.add_process(p)
    stcf.run()

    print_comparison(
        [sjf.stats, stcf.stats],
        processes_sjf
    )

    print("\nCONCLUSION:")
    print("SJF picks the shortest job available but never preempts.")
    print("STCF preempts whenever a shorter job arrives — better")
    print("response time but more context switches.")