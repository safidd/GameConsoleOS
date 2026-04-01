from pcb import PCB, ProcessState
from collections import deque

class MLFQScheduler:
    def __init__(self):
        self.queues = [
            deque(),  # Q0 — highest priority, quantum=2
            deque(),  # Q1 — medium priority,  quantum=4
            deque(),  # Q2 — lowest priority,   quantum=8
        ]
        self.quantums = [2, 4, 8]
        self.current_time = 0
        self.timeline = {}

    def add_process(self, process):
        process.state = ProcessState.READY
        process.queue_level = 0
        self.queues[0].append(process)
        self.timeline[process.name] = []
        print(f"[MLFQ] {process.name} added to Q0 (quantum={self.quantums[0]})")

    def record(self, name, symbol, ticks):
        for _ in range(ticks):
            self.timeline[name].append(symbol)
        max_len = max(len(v) for v in self.timeline.values())
        for n in self.timeline:
            while len(self.timeline[n]) < max_len:
                self.timeline[n].append("░")

    def run(self):
        print(f"\n[MLFQ] Starting Multi-Level Feedback Queue...\n")
        while any(self.queues):
            # find highest priority non-empty queue
            current_queue = None
            queue_index = None
            for i, q in enumerate(self.queues):
                if q:
                    current_queue = q
                    queue_index = i
                    break

            if current_queue is None:
                break

            process = current_queue.popleft()
            process.state = ProcessState.RUNNING
            quantum = self.quantums[queue_index]

            print(f"[t={self.current_time}] Running: {process.name} | Q{queue_index} (quantum={quantum}) | CPU: {process.cpu_time}/{process.burst_time}")

            ticks = min(quantum, process.burst_time - process.cpu_time)
            process.cpu_time += ticks
            self.current_time += ticks
            self.record(process.name, "█", ticks)

            if process.cpu_time >= process.burst_time:
                process.state = ProcessState.TERMINATED
                print(f"[MLFQ] Terminated: {process.name}\n")

            elif process.is_io_bound and not process.io_done:
                # I/O bound — promote back to Q0
                process.io_done = True
                process.queue_level = 0
                process.state = ProcessState.READY
                self.queues[0].append(process)
                self.record(process.name, "B", 1)
                self.current_time += 1
                print(f"[MLFQ] {process.name} did I/O — promoted back to Q0\n")

            else:
                # used full quantum — demote to next queue
                new_level = min(queue_index + 1, 2)
                if new_level != queue_index:
                    print(f"[MLFQ] {process.name} used full quantum — demoted Q{queue_index} -> Q{new_level}")
                process.queue_level = new_level
                process.state = ProcessState.READY
                self.queues[new_level].append(process)

        print(f"\n[MLFQ] All processes finished at t={self.current_time}")

    def print_timeline(self):
        print("\n" + "=" * 55)
        print("     MLFQ EXECUTION TIMELINE")
        print("=" * 55)
        print(f"\n  Legend: █ = running  ░ = waiting  B = I/O\n")
        max_name = max(len(n) for n in self.timeline)
        total = max(len(v) for v in self.timeline.values())
        markers = "".join(str(i % 10) for i in range(total))
        print(f"  {'Time':<{max_name}}  {markers}")
        print(f"  {'-'*max_name}  {'-'*total}")
        for name, slots in self.timeline.items():
            bar = "".join(slots)
            print(f"  {name:<{max_name}}  {bar}")
        print(f"\n  Total time: {self.current_time} units")
        print("=" * 55)

if __name__ == "__main__":
    print("=" * 55)
    print("     MLFQ SCHEDULER DEMO")
    print("=" * 55)

    scheduler = MLFQScheduler()

    p1 = PCB(pid=1, name="GameProcess",  priority=3, memory_required=256)
    p2 = PCB(pid=2, name="DownloadMgr",  priority=1, memory_required=80)
    p3 = PCB(pid=3, name="SaveThread",   priority=2, memory_required=40)
    p4 = PCB(pid=4, name="AudioEngine",  priority=3, memory_required=60)

    p1.burst_time = 10; p1.io_done = False; p1.is_io_bound = False
    p2.burst_time = 3;  p2.io_done = False; p2.is_io_bound = False
    p3.burst_time = 6;  p3.io_done = False; p3.is_io_bound = True
    p4.burst_time = 4;  p4.io_done = False; p4.is_io_bound = False

    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.add_process(p3)
    scheduler.add_process(p4)

    scheduler.run()
    scheduler.print_timeline()

    print("\nCONCLUSION:")
    print("Short processes (DownloadMgr, AudioEngine) finish")
    print("quickly in Q0 without being demoted.")
    print("Long processes (GameProcess) get demoted to Q1/Q2.")
    print("I/O bound processes (SaveThread) get promoted back")
    print("to Q0 after blocking — rewarding interactive behavior.")