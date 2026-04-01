from pcb import PCB, ProcessState
from rr_scheduler import RoundRobinScheduler
from memory_manager import MemoryManager

print("=" * 55)
print("     STRESS TEST — Heavy Load Simulation")
print("=" * 55)

# Boot OS with limited memory
mem = MemoryManager(total_memory=512)
scheduler = RoundRobinScheduler(time_quantum=2)

# Create 10 processes — double the normal load
processes = [
    PCB(pid=1,  name="GameProcess",      priority=3, memory_required=256),
    PCB(pid=2,  name="DownloadManager",  priority=1, memory_required=80),
    PCB(pid=3,  name="SaveThread",       priority=2, memory_required=40),
    PCB(pid=4,  name="ScreenshotSvc",    priority=1, memory_required=30),
    PCB(pid=5,  name="AudioEngine",      priority=3, memory_required=60),
    PCB(pid=6,  name="NetworkSync",      priority=1, memory_required=50),
    PCB(pid=7,  name="AchievementSvc",   priority=1, memory_required=30),
    PCB(pid=8,  name="VideoCapture",     priority=2, memory_required=90),
    PCB(pid=9,  name="CloudBackup",      priority=1, memory_required=70),
    PCB(pid=10, name="UpdateChecker",    priority=1, memory_required=40),
]

burst_times  = [5, 3, 4, 2, 3, 2, 1, 4, 3, 2]
io_processes = [3, 8]  # SaveThread and VideoCapture do I/O

for i, p in enumerate(processes):
    p.burst_time = burst_times[i]
    p.io_done = False
    p.is_io_bound = p.pid in io_processes
    p.memory_manager = mem

print(f"\n[Stress] Launching {len(processes)} processes on 512MB RAM...\n")

allocated = []
rejected  = []

print("--- Memory Allocation Phase ---\n")
for p in processes:
    success = mem.allocate(p)
    if success:
        allocated.append(p)
    else:
        print(f"[Stress] Attempting exhaustion handling for {p.name}...")
        mem.handle_exhaustion(p, allocated)
        retry = mem.allocate(p)
        if retry:
            allocated.append(p)
        else:
            rejected.append(p)
            print(f"[Stress] {p.name} could NOT be allocated — rejected\n")

mem.status()

print(f"\n[Stress] Successfully loaded: {len(allocated)} processes")
print(f"[Stress] Rejected due to memory: {len(rejected)} processes")
if rejected:
    for r in rejected:
        print(f"  - {r.name}")

print("\n--- Scheduling Phase ---\n")
for p in allocated:
    if p.state != ProcessState.TERMINATED:
        scheduler.add_process(p)

scheduler.run()

print("\n--- Final Process Status ---\n")
terminated = [p for p in processes if p.state == ProcessState.TERMINATED]
print(f"[Stress] Total processes: {len(processes)}")
print(f"[Stress] Completed: {len(terminated)}")
print(f"[Stress] Rejected: {len(rejected)}")

print("\n--- Final Memory Status ---")
mem.status()

print("\n" + "=" * 55)
print("STRESS TEST CONCLUSION:")
print(f"System handled {len(processes)} processes on 512MB RAM.")
if rejected:
    print(f"{len(rejected)} process(es) rejected — memory too full.")
    print("Behavior: exhaustion handler killed lowest priority")
    print("processes to make room. System stayed alive.")
else:
    print("All processes allocated and scheduled successfully.")
print("=" * 55)