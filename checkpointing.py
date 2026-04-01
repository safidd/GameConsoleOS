import json
import os
from pcb import PCB, ProcessState
from memory_manager import MemoryManager

CHECKPOINT_DIR = "checkpoints"

class CheckpointManager:
    def __init__(self):
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    def save(self, process):
        checkpoint = {
            "pid":             process.pid,
            "name":            process.name,
            "priority":        process.priority,
            "memory_required": process.memory_required,
            "cpu_time":        process.cpu_time,
            "burst_time":      process.burst_time,
            "state":           process.state,
        }
        path = f"{CHECKPOINT_DIR}/{process.name}_pid{process.pid}.json"
        with open(path, "w") as f:
            json.dump(checkpoint, f, indent=2)
        print(f"[Checkpoint] Saved state of {process.name} to {path}")
        return path

    def restore(self, name, pid):
        path = f"{CHECKPOINT_DIR}/{name}_pid{pid}.json"
        if not os.path.exists(path):
            print(f"[Checkpoint] ERROR: No checkpoint found for {name}")
            return None
        with open(path, "r") as f:
            data = json.load(f)
        process = PCB(
            pid=data["pid"],
            name=data["name"],
            priority=data["priority"],
            memory_required=data["memory_required"]
        )
        process.cpu_time  = data["cpu_time"]
        process.burst_time = data["burst_time"]
        process.state     = ProcessState.READY
        process.io_done   = False
        process.is_io_bound = False
        print(f"[Checkpoint] Restored {process.name} — CPU progress: {process.cpu_time}/{process.burst_time}")
        return process

    def list_checkpoints(self):
        files = os.listdir(CHECKPOINT_DIR)
        if not files:
            print("[Checkpoint] No checkpoints saved.")
            return
        print(f"\n[Checkpoint] Saved checkpoints ({len(files)}):")
        for f in files:
            print(f"  {f}")

class CheckpointMemoryManager(MemoryManager):
    def __init__(self, total_memory, checkpoint_manager):
        super().__init__(total_memory)
        self.checkpoint_manager = checkpoint_manager

    def handle_exhaustion(self, process, processes):
        print(f"\n[Memory] MEMORY EXHAUSTION -- need {process.memory_required}MB, only {self.available_memory}MB free!")
        candidates = [p for p in processes if p.pid in self.memory_map and p.pid != process.pid]
        while self.available_memory < process.memory_required and candidates:
            victim = min(candidates, key=lambda p: p.priority)
            # save checkpoint before killing
            self.checkpoint_manager.save(victim)
            victim.state = ProcessState.TERMINATED
            self.deallocate(victim)
            candidates.remove(victim)
            print(f"[Memory] Killed {victim.name} (PID:{victim.pid}) -- state saved to checkpoint")
            print(f"[Memory] Available memory now: {self.available_memory}MB\n")

if __name__ == "__main__":
    print("=" * 55)
    print("     PROCESS CHECKPOINTING DEMO")
    print("=" * 55)

    cp = CheckpointManager()
    mem = CheckpointMemoryManager(total_memory=512, checkpoint_manager=cp)

    p1 = PCB(pid=1, name="GameProcess",   priority=3, memory_required=256)
    p2 = PCB(pid=2, name="DownloadMgr",   priority=1, memory_required=128)
    p3 = PCB(pid=3, name="SaveThread",    priority=2, memory_required=64)
    p4 = PCB(pid=4, name="VideoCapture",  priority=2, memory_required=250)

    for p in [p1,p2,p3,p4]:
        p.burst_time = 5
        p.cpu_time = 2  # simulate partially run processes

    all_processes = [p1, p2, p3]

    print("\n--- Phase 1: Allocate initial processes ---\n")
    for p in all_processes:
        mem.allocate(p)
    mem.status()

    print("\n--- Phase 2: VideoCapture needs 250MB — memory exhaustion ---\n")
    success = mem.allocate(p4)
    if not success:
        mem.handle_exhaustion(p4, all_processes)
        mem.allocate(p4)

    mem.status()
    cp.list_checkpoints()

    print("\n--- Phase 3: Restore killed processes when memory frees up ---\n")
    mem.deallocate(p4)
    print(f"[OS] VideoCapture finished — freed memory\n")

    restored = cp.restore("DownloadMgr", 2)
    if restored:
        mem.allocate(restored)
        print(f"[OS] {restored.name} restored — will resume from CPU time {restored.cpu_time}/{restored.burst_time}")

    mem.status()

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("Before killing a process, OS saves its state.")
    print("When memory is available again, process is")
    print("restored and continues from where it left off.")
    print("=" * 55)