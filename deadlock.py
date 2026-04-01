from pcb import PCB, ProcessState

class Resource:
    def __init__(self, name):
        self.name = name
        self.held_by = None
        self.waiting = []

    def __repr__(self):
        return f"[Resource: {self.name} | held by: {self.held_by.name if self.held_by else 'free'}]"

class DeadlockDetector:
    def __init__(self):
        self.resources = {}
        self.processes = []

    def add_resource(self, resource):
        self.resources[resource.name] = resource

    def add_process(self, process):
        self.processes.append(process)
        process.holds = []
        process.wants = None

    def acquire(self, process, resource):
        if resource.held_by is None:
            resource.held_by = process
            process.holds.append(resource)
            print(f"[Lock] {process.name} acquired '{resource.name}'")
            return True
        else:
            resource.waiting.append(process)
            process.wants = resource
            print(f"[Lock] {process.name} WAITING for '{resource.name}' (held by {resource.held_by.name})")
            return False

    def detect_deadlock(self):
        print(f"\n[Deadlock] Running cycle detection...")
        for process in self.processes:
            if process.wants is None:
                continue
            visited = set()
            current = process
            while current is not None:
                if current in visited:
                    print(f"[Deadlock] DEADLOCK DETECTED — cycle found!")
                    return True
                visited.add(current)
                wanted = current.wants
                if wanted is None:
                    break
                current = wanted.held_by
        print(f"[Deadlock] No deadlock detected.")
        return False

    def resolve_deadlock(self):
        print(f"\n[Deadlock] Resolving — killing lowest priority process in cycle...")
        candidates = [p for p in self.processes if p.wants is not None]
        if not candidates:
            return
        victim = min(candidates, key=lambda p: p.priority)
        print(f"[Deadlock] Killing {victim.name} (priority {victim.priority})")

        # release all resources held by victim
        for resource in list(victim.holds):
            resource.held_by = None
            victim.holds.remove(resource)
            print(f"[Deadlock] {victim.name} released '{resource.name}'")

            # give resource to next waiting process
            if resource.waiting:
                next_process = resource.waiting.pop(0)
                next_process.wants = None
                resource.held_by = next_process
                next_process.holds.append(resource)
                print(f"[Deadlock] '{resource.name}' given to {next_process.name}")

        victim.state = ProcessState.TERMINATED
        victim.wants = None
        print(f"[Deadlock] {victim.name} terminated — deadlock resolved\n")

    def show_state(self):
        print(f"\n[Deadlock] Current resource state:")
        for r in self.resources.values():
            print(f"  {r}")
        print(f"[Deadlock] Current process state:")
        for p in self.processes:
            holds = [r.name for r in p.holds]
            wants = p.wants.name if p.wants else "nothing"
            print(f"  {p.name} | holds: {holds} | wants: {wants}")

if __name__ == "__main__":
    print("=" * 55)
    print("     DEADLOCK DETECTION & RESOLUTION DEMO")
    print("=" * 55)

    detector = DeadlockDetector()

    # Resources
    save_lock    = Resource("save_file_lock")
    network_lock = Resource("network_lock")
    detector.add_resource(save_lock)
    detector.add_resource(network_lock)

    # Processes
    p1 = PCB(pid=1, name="GameProcess",    priority=3, memory_required=256)
    p2 = PCB(pid=2, name="CloudBackup",    priority=1, memory_required=70)
    detector.add_process(p1)
    detector.add_process(p2)

    print("\n--- Setting up deadlock ---\n")
    print("[OS] GameProcess acquires save_file_lock, then wants network_lock")
    print("[OS] CloudBackup acquires network_lock, then wants save_file_lock\n")

    # GameProcess gets save lock, CloudBackup gets network lock
    detector.acquire(p1, save_lock)
    detector.acquire(p2, network_lock)

    # Now they want each other's lock — deadlock!
    detector.acquire(p1, network_lock)
    detector.acquire(p2, save_lock)

    detector.show_state()

    # Detect
    deadlock_found = detector.detect_deadlock()

    if deadlock_found:
        detector.resolve_deadlock()
        detector.show_state()

        # Check again
        print("[Deadlock] Verifying resolution...")
        detector.detect_deadlock()

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("GameProcess and CloudBackup were deadlocked.")
    print("Detector found the cycle, killed lowest priority")
    print("process (CloudBackup), released its locks,")
    print("and GameProcess could continue.")
    print("=" * 55)