from pcb import PCB, ProcessState
import time

class ProcessTree:
    def __init__(self):
        self.processes = {}   # pid -> process
        self.children  = {}   # pid -> [child pids]
        self.parent    = {}   # pid -> parent pid
        self.next_pid  = 1

    def create(self, name, priority, memory_required, parent_pid=None):
        pid = self.next_pid
        self.next_pid += 1
        process = PCB(pid=pid, name=name, priority=priority, memory_required=memory_required)
        process.created_at = time.time()
        process.state = ProcessState.READY
        self.processes[pid] = process
        self.children[pid] = []
        if parent_pid is not None:
            self.parent[pid] = parent_pid
            self.children[parent_pid].append(pid)
            parent = self.processes[parent_pid]
            print(f"[Fork] {parent.name} (PID:{parent_pid}) forked -> {name} (PID:{pid})")
        else:
            self.parent[pid] = None
            print(f"[Init] Created root process {name} (PID:{pid})")
        return process

    def terminate(self, pid):
        process = self.processes[pid]
        # terminate all children first
        for child_pid in list(self.children[pid]):
            self.terminate(child_pid)
        process.state = ProcessState.TERMINATED
        parent_pid = self.parent[pid]
        if parent_pid:
            self.children[parent_pid].remove(pid)
            print(f"[Exit] {process.name} (PID:{pid}) terminated — parent: {self.processes[parent_pid].name}")
        else:
            print(f"[Exit] {process.name} (PID:{pid}) terminated — root process")

    def print_tree(self, pid=None, indent=0):
        if pid is None:
            # find root
            roots = [p for p in self.processes if self.parent[p] is None]
            for r in roots:
                self.print_tree(r, 0)
            return
        process = self.processes[pid]
        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        print(f"{prefix}{process.name} (PID:{pid}) [{process.state}] priority={process.priority}")
        for child_pid in self.children[pid]:
            self.print_tree(child_pid, indent + 1)

    def show_stats(self):
        total = len(self.processes)
        running    = sum(1 for p in self.processes.values() if p.state == ProcessState.RUNNING)
        ready      = sum(1 for p in self.processes.values() if p.state == ProcessState.READY)
        terminated = sum(1 for p in self.processes.values() if p.state == ProcessState.TERMINATED)
        print(f"\n[Tree] Total: {total} | Ready: {ready} | Running: {running} | Terminated: {terminated}")

if __name__ == "__main__":
    print("=" * 55)
    print("     PROCESS FAMILY TREE DEMO")
    print("=" * 55)

    tree = ProcessTree()

    print("\n--- Phase 1: Boot — create init process ---\n")
    init = tree.create("SystemInit", priority=3, memory_required=32)

    print("\n--- Phase 2: SystemInit forks core processes ---\n")
    game    = tree.create("GameProcess",   priority=3, memory_required=256, parent_pid=init.pid)
    audio   = tree.create("AudioEngine",   priority=3, memory_required=60,  parent_pid=init.pid)
    network = tree.create("NetworkMgr",    priority=2, memory_required=50,  parent_pid=init.pid)

    print("\n--- Phase 3: GameProcess forks child processes ---\n")
    render  = tree.create("RenderThread",  priority=3, memory_required=80,  parent_pid=game.pid)
    physics = tree.create("PhysicsThread", priority=2, memory_required=60,  parent_pid=game.pid)
    save    = tree.create("SaveThread",    priority=2, memory_required=40,  parent_pid=game.pid)

    print("\n--- Phase 4: NetworkMgr forks child processes ---\n")
    download = tree.create("DownloadMgr",  priority=1, memory_required=80,  parent_pid=network.pid)
    cloud    = tree.create("CloudBackup",  priority=1, memory_required=70,  parent_pid=network.pid)

    print("\n--- Process Tree ---\n")
    tree.print_tree()
    tree.show_stats()

    print("\n--- Phase 5: Game ends — GameProcess terminates with all children ---\n")
    tree.terminate(game.pid)

    print("\n--- Updated Process Tree ---\n")
    tree.print_tree()
    tree.show_stats()

    print("\n--- Phase 6: System shutdown ---\n")
    tree.terminate(init.pid)

    print("\n--- Final Process Tree ---\n")
    tree.print_tree()
    tree.show_stats()

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("fork() creates parent-child relationships.")
    print("When a parent terminates, all children")
    print("are terminated first — clean shutdown.")
    print("=" * 55)