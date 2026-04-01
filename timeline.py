from pcb import PCB, ProcessState
from collections import deque

class TimelineScheduler:
    def __init__(self, time_quantum=2):
        self.ready_queue = deque()
        self.blocked_queue = []
        self.time_quantum = time_quantum
        self.timeline = {}
        self.current_time = 0

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        self.timeline[process.name] = []

    def record(self, process, symbol):
        self.timeline[process.name].append(symbol)
        for p in self.ready_queue:
            if p != process and len(self.timeline[p.name]) < len(self.timeline[process.name]):
                self.timeline[p.name].append("░")
        for p in self.blocked_queue:
            if len(self.timeline[p.name]) < len(self.timeline[process.name]):
                self.timeline[p.name].append("B")

    def unblock_all(self):
        for process in list(self.blocked_queue):
            self.blocked_queue.remove(process)
            process.state = ProcessState.READY
            self.ready_queue.append(process)

    def run(self):
        print(f"\n[Scheduler] Starting Round Robin (quantum={self.time_quantum})...\n")
        all_processes = list(self.ready_queue)

        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.state = ProcessState.RUNNING

            if process.is_io_bound and not process.io_done:
                process.state = ProcessState.BLOCKED
                process.io_done = True
                self.blocked_queue.append(process)
                self.record(process, "B")
                self.current_time += 1
                print(f"[t={self.current_time}] {process.name} BLOCKED (I/O)")
                self.unblock_all()
                continue

            ticks = min(self.time_quantum, process.burst_time - process.cpu_time)
            for _ in range(ticks):
                self.record(process, "█")
                self.current_time += 1

            process.cpu_time += ticks
            print(f"[t={self.current_time}] {process.name} ran {ticks} units (total: {process.cpu_time}/{process.burst_time})")

            if process.cpu_time >= process.burst_time:
                process.state = ProcessState.TERMINATED
                print(f"[t={self.current_time}] {process.name} TERMINATED")
            else:
                process.state = ProcessState.READY
                self.ready_queue.append(process)

        # pad all timelines to same length
        max_len = max(len(v) for v in self.timeline.values())
        for name in self.timeline:
            while len(self.timeline[name]) < max_len:
                self.timeline[name].append("░")

    def print_timeline(self):
        print("\n" + "=" * 55)
        print("     PROCESS EXECUTION TIMELINE")
        print("=" * 55)
        print(f"\n  Legend: █ = running  ░ = waiting  B = blocked\n")

        max_name = max(len(n) for n in self.timeline)
        total = len(next(iter(self.timeline.values())))

        # time markers
        markers = "".join(str(i % 10) for i in range(total))
        print(f"  {'Time':<{max_name}}  {markers}")
        print(f"  {'-'*max_name}  {'-'*total}")

        for name, slots in self.timeline.items():
            bar = "".join(slots)
            print(f"  {name:<{max_name}}  {bar}")

        print(f"\n  Total time units: {self.current_time}")
        print("=" * 55)

if __name__ == "__main__":
    print("=" * 55)
    print("     TIMELINE VISUALIZATION DEMO")
    print("=" * 55)

    scheduler = TimelineScheduler(time_quantum=2)

    p1 = PCB(pid=1, name="GameProcess",    priority=3, memory_required=256)
    p2 = PCB(pid=2, name="DownloadMgr",    priority=1, memory_required=128)
    p3 = PCB(pid=3, name="SaveThread",     priority=2, memory_required=64)
    p4 = PCB(pid=4, name="AudioEngine",    priority=3, memory_required=60)

    p1.burst_time = 5; p1.io_done = False; p1.is_io_bound = False
    p2.burst_time = 3; p2.io_done = False; p2.is_io_bound = False
    p3.burst_time = 4; p3.io_done = False; p3.is_io_bound = True
    p4.burst_time = 3; p4.io_done = False; p4.is_io_bound = False

    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.add_process(p3)
    scheduler.add_process(p4)

    scheduler.run()
    scheduler.print_timeline()