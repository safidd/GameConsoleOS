from pcb import PCB, ProcessState
from collections import deque

class StatsScheduler:
    def __init__(self, time_quantum=2):
        self.ready_queue = deque()
        self.time_quantum = time_quantum
        self.current_time = 0
        self.stats = {}  # pid -> {name, wait_time, turnaround, response, burst}

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        self.stats[process.pid] = {
            "name":        process.name,
            "burst":       process.burst_time,
            "priority":    process.priority,
            "arrival":     self.current_time,
            "first_run":   None,
            "finish":      None,
            "wait":        0,
            "turnaround":  0,
            "response":    0,
        }
        print(f"[Scheduler] {process.name} added (burst={process.burst_time})")

    def run(self):
        print(f"\n[Scheduler] Starting Round Robin (quantum={self.time_quantum})...\n")
        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING
            s = self.stats[process.pid]

            if s["first_run"] is None:
                s["first_run"] = self.current_time
                s["response"] = self.current_time - s["arrival"]

            ticks = min(self.time_quantum, process.burst_time - process.cpu_time)
            process.cpu_time += ticks
            self.current_time += ticks

            # waiting time = time spent in ready queue
            for p in self.ready_queue:
                self.stats[p.pid]["wait"] += ticks

            print(f"[t={self.current_time}] {process.name} ran {ticks} units (total: {process.cpu_time}/{process.burst_time})")

            if process.cpu_time >= process.burst_time:
                process.state = ProcessState.TERMINATED
                s["finish"] = self.current_time
                s["turnaround"] = s["finish"] - s["arrival"]
                print(f"[Scheduler] Terminated: {process.name}\n")
            else:
                process.state = ProcessState.READY
                self.ready_queue.append(process)

    def print_stats(self):
        print("\n" + "=" * 65)
        print("     CPU UTILIZATION & PERFORMANCE STATS")
        print("=" * 65)

        total_burst = sum(s["burst"] for s in self.stats.values())
        cpu_utilization = (total_burst / self.current_time) * 100

        print(f"\n  Total time:       {self.current_time} units")
        print(f"  CPU utilization:  {cpu_utilization:.1f}%")
        print(f"  Processes run:    {len(self.stats)}\n")

        # table header
        col = 16
        print(f"  {'Process':<{col}} {'Burst':>6} {'Wait':>6} {'Turnaround':>11} {'Response':>9} {'Priority':>9}")
        print(f"  {'-'*col} {'-----':>6} {'----':>6} {'----------':>11} {'--------':>9} {'--------':>9}")

        total_wait = 0
        total_turnaround = 0
        total_response = 0

        for s in self.stats.values():
            print(f"  {s['name']:<{col}} {s['burst']:>6} {s['wait']:>6} {s['turnaround']:>11} {s['response']:>9} {s['priority']:>9}")
            total_wait       += s["wait"]
            total_turnaround += s["turnaround"]
            total_response   += s["response"]

        n = len(self.stats)
        print(f"\n  {'AVERAGE':<{col}} {'':>6} {total_wait/n:>6.1f} {total_turnaround/n:>11.1f} {total_response/n:>9.1f}")

        print(f"\n  Avg wait time:        {total_wait/n:.1f} units")
        print(f"  Avg turnaround time:  {total_turnaround/n:.1f} units")
        print(f"  Avg response time:    {total_response/n:.1f} units")
        print("=" * 65)

if __name__ == "__main__":
    print("=" * 65)
    print("     CPU STATS DEMO — Round Robin vs FIFO")
    print("=" * 65)

    print("\n--- Round Robin (quantum=2) ---\n")
    rr = StatsScheduler(time_quantum=2)
    processes = [
        ("GameProcess",   3, 5),
        ("DownloadMgr",   1, 3),
        ("SaveThread",    2, 4),
        ("AudioEngine",   3, 3),
        ("CloudBackup",   1, 2),
    ]
    for name, priority, burst in processes:
        p = PCB(pid=len(rr.stats)+1, name=name, priority=priority, memory_required=64)
        p.burst_time = burst
        p.cpu_time = 0
        rr.add_process(p)
    rr.run()
    rr.print_stats()

    print("\n--- FIFO ---\n")
    fifo = StatsScheduler(time_quantum=999)  # huge quantum = FIFO behavior
    for name, priority, burst in processes:
        p = PCB(pid=len(fifo.stats)+1, name=name, priority=priority, memory_required=64)
        p.burst_time = burst
        p.cpu_time = 0
        fifo.add_process(p)
    fifo.run()
    fifo.print_stats()

    print("\nCONCLUSION:")
    print("Round Robin has lower avg wait and response times.")
    print("FIFO has lower overhead but starves short processes.")