from pcb import PCB, ProcessState
from rr_scheduler import RoundRobinScheduler
from memory_manager import MemoryManager

print("=" * 55)
print("       🎮 GAME CONSOLE OS — SIMULATION START")
print("=" * 55)

# Boot the OS
mem = MemoryManager(total_memory=512)
scheduler = RoundRobinScheduler(time_quantum=2)

# Create processes
p1 = PCB(pid=1, name="GameProcess",       priority=3, memory_required=256)
p2 = PCB(pid=2, name="DownloadManager",   priority=1, memory_required=128)
p3 = PCB(pid=3, name="SaveThread",        priority=2, memory_required=64)
p4 = PCB(pid=4, name="ScreenshotService", priority=1, memory_required=200)

p1.burst_time = 5; p1.io_done = False; p1.is_io_bound = False
p2.burst_time = 3; p2.io_done = False; p2.is_io_bound = False
p3.burst_time = 4; p3.io_done = False; p3.is_io_bound = True
p4.burst_time = 2; p4.io_done = False; p4.is_io_bound = False

all_processes = [p1, p2, p3, p4]

# Link memory manager to every process
for p in all_processes:
    p.memory_manager = mem

print("\n--- PHASE 1: Memory Allocation ---\n")
for p in [p1, p2, p3]:
    success = mem.allocate(p)
    if not success:
        mem.handle_exhaustion(p, all_processes)
        mem.allocate(p)

mem.status()

print("\n--- PHASE 2: Scheduling ---\n")
for p in [p1, p2, p3]:
    scheduler.add_process(p)

scheduler.run()

print("\n--- PHASE 3: Failure Scenario — ScreenshotService Launch ---\n")
print("[OS] User launched ScreenshotService while memory is full...")
success = mem.allocate(p4)
if not success:
    mem.handle_exhaustion(p4, all_processes)
    mem.allocate(p4)
scheduler.add_process(p4)
scheduler.run()