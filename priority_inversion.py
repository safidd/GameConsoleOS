import time
from pcb import PCB, ProcessState

class Mutex:
    def __init__(self, name):
        self.name = name
        self.held_by = None

    def acquire(self, process):
        if self.held_by is None:
            self.held_by = process
            print(f"[Lock] {process.name} acquired lock '{self.name}'")
            return True
        else:
            print(f"[Lock] {process.name} WAITING — lock '{self.name}' held by {self.held_by.name}")
            return False

    def release(self, process):
        if self.held_by == process:
            print(f"[Lock] {process.name} released lock '{self.name}'")
            self.held_by = None

class PriorityScheduler:
    def __init__(self):
        self.processes = []

    def add_process(self, process):
        self.processes.append(process)
        print(f"[Scheduler] Added {process.name} (priority {process.priority})")

    def run_without_inheritance(self, lock):
        print("\n--- WITHOUT Priority Inheritance (Inversion occurs) ---\n")
        time_unit = 0

        # Low priority acquires lock first
        low = next(p for p in self.processes if p.priority == 1)
        lock.acquire(low)

        for _ in range(6):
            time_unit += 1
            # find highest priority non-terminated process
            candidates = [p for p in self.processes if p.state != ProcessState.TERMINATED]
            if not candidates:
                break
            # sort by priority descending
            candidates.sort(key=lambda p: p.priority, reverse=True)
            current = candidates[0]

            # high priority needs lock but can't get it
            high = next((p for p in candidates if p.priority == 3), None)
            if high and lock.held_by and lock.held_by != high:
                if not lock.acquire(high):
                    # high is blocked — medium runs instead
                    medium = next((p for p in candidates if p.priority == 2), None)
                    if medium:
                        medium.state = ProcessState.RUNNING
                        medium.cpu_time += 1
                        print(f"[Time {time_unit}] Running: {medium.name} (priority {medium.priority}) — HIGH priority process is stuck!")
                        if medium.cpu_time >= medium.burst_time:
                            medium.state = ProcessState.TERMINATED
                            print(f"[Scheduler] Terminated: {medium.name}")
                        else:
                            medium.state = ProcessState.READY
                        continue

            # low priority runs to finish and release lock
            if lock.held_by == low and low.state != ProcessState.TERMINATED:
                low.state = ProcessState.RUNNING
                low.cpu_time += 1
                print(f"[Time {time_unit}] Running: {low.name} (priority {low.priority})")
                if low.cpu_time >= low.burst_time:
                    low.state = ProcessState.TERMINATED
                    lock.release(low)
                    print(f"[Scheduler] Terminated: {low.name}")
                else:
                    low.state = ProcessState.READY
                continue

            # normal scheduling
            current.state = ProcessState.RUNNING
            current.cpu_time += 1
            print(f"[Time {time_unit}] Running: {current.name} (priority {current.priority})")
            if current.cpu_time >= current.burst_time:
                current.state = ProcessState.TERMINATED
                print(f"[Scheduler] Terminated: {current.name}")
            else:
                current.state = ProcessState.READY

    def run_with_inheritance(self, lock):
        print("\n--- WITH Priority Inheritance (Inversion resolved) ---\n")

        # reset all processes
        for p in self.processes:
            p.state = ProcessState.READY
            p.cpu_time = 0

        time_unit = 0
        low = next(p for p in self.processes if p.priority == 1)
        original_priority = low.priority
        lock.held_by = None
        lock.acquire(low)

        for _ in range(6):
            time_unit += 1
            candidates = [p for p in self.processes if p.state != ProcessState.TERMINATED]
            if not candidates:
                break

            high = next((p for p in candidates if p.priority == 3), None)

            # priority inheritance: boost low priority to match high
            if high and lock.held_by == low:
                if low.priority < high.priority:
                    low.priority = high.priority
                    print(f"[Inheritance] Boosting {low.name} priority to {low.priority} so it can finish faster")

            # low runs first to release lock
            if lock.held_by == low and low.state != ProcessState.TERMINATED:
                low.state = ProcessState.RUNNING
                low.cpu_time += 1
                print(f"[Time {time_unit}] Running: {low.name} (boosted priority {low.priority})")
                if low.cpu_time >= low.burst_time:
                    low.state = ProcessState.TERMINATED
                    low.priority = original_priority
                    lock.release(low)
                    print(f"[Scheduler] Terminated: {low.name} — lock released, restoring priority to {original_priority}")
                else:
                    low.state = ProcessState.READY
                continue

            # now high can run
            candidates.sort(key=lambda p: p.priority, reverse=True)
            current = candidates[0]
            current.state = ProcessState.RUNNING
            current.cpu_time += 1
            print(f"[Time {time_unit}] Running: {current.name} (priority {current.priority})")
            if current.cpu_time >= current.burst_time:
                current.state = ProcessState.TERMINATED
                print(f"[Scheduler] Terminated: {current.name}")
            else:
                current.state = ProcessState.READY

if __name__ == "__main__":
    print("=" * 55)
    print("     PRIORITY INVERSION DEMO")
    print("=" * 55)

    lock = Mutex("save_file_lock")

    p1 = PCB(pid=1, name="GameProcess",     priority=3, memory_required=256)
    p2 = PCB(pid=2, name="SaveThread",      priority=2, memory_required=64)
    p3 = PCB(pid=3, name="DownloadManager", priority=1, memory_required=128)

    p1.burst_time = 3
    p2.burst_time = 2
    p3.burst_time = 3

    scheduler = PriorityScheduler()
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.add_process(p3)

    scheduler.run_without_inheritance(lock)

    print()
    lock2 = Mutex("save_file_lock")
    scheduler2 = PriorityScheduler()

    q1 = PCB(pid=1, name="GameProcess",     priority=3, memory_required=256)
    q2 = PCB(pid=2, name="SaveThread",      priority=2, memory_required=64)
    q3 = PCB(pid=3, name="DownloadManager", priority=1, memory_required=128)

    q1.burst_time = 3
    q2.burst_time = 2
    q3.burst_time = 3

    scheduler2.add_process(q1)
    scheduler2.add_process(q2)
    scheduler2.add_process(q3)

    scheduler2.run_with_inheritance(lock2)

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("Without inheritance: medium priority runs while")
    print("high priority is stuck — classic priority inversion.")
    print("With inheritance: low priority gets boosted,")
    print("finishes fast, releases lock, high priority runs.")
    print("=" * 55)