from pcb import PCB, ProcessState
from rr_scheduler import RoundRobinScheduler
from memory_manager import MemoryManager
from timeline import TimelineScheduler

print("\n" + "=" * 55)
print("     🎮 GAME CONSOLE OS — FULL SIMULATION")
print("=" * 55)

# ── BOOT ──────────────────────────────────────────────
print("\n>>> PHASE 1: SYSTEM BOOT\n")
mem = MemoryManager(total_memory=512)
print("[OS] Memory Manager online — 512MB RAM")
print("[OS] Scheduler online")
print("[OS] NOTE: File system and page fault modules")
print("[OS]       will be added by teammates")

# ── PROCESSES ─────────────────────────────────────────
print("\n>>> PHASE 2: PROCESS CREATION\n")
p1 = PCB(pid=1, name="GameProcess",   priority=3, memory_required=256)
p2 = PCB(pid=2, name="DownloadMgr",   priority=1, memory_required=80)
p3 = PCB(pid=3, name="SaveThread",    priority=2, memory_required=40)
p4 = PCB(pid=4, name="AudioEngine",   priority=3, memory_required=60)
p5 = PCB(pid=5, name="CloudBackup",   priority=1, memory_required=70)

p1.burst_time = 5; p1.io_done = False; p1.is_io_bound = False
p2.burst_time = 3; p2.io_done = False; p2.is_io_bound = False
p3.burst_time = 4; p3.io_done = False; p3.is_io_bound = True
p4.burst_time = 3; p4.io_done = False; p4.is_io_bound = False
p5.burst_time = 3; p5.io_done = False; p5.is_io_bound = False

all_processes = [p1, p2, p3, p4, p5]
for p in all_processes:
    p.memory_manager = mem
    print(f"[OS] Created {p}")

# ── MEMORY ALLOCATION ─────────────────────────────────
print("\n>>> PHASE 3: MEMORY ALLOCATION\n")
allocated = []
for p in all_processes:
    success = mem.allocate(p)
    if success:
        allocated.append(p)
    else:
        mem.handle_exhaustion(p, allocated)
        if mem.allocate(p):
            allocated.append(p)
mem.status()

# ── SCHEDULING + TIMELINE ─────────────────────────────
print("\n>>> PHASE 4: SCHEDULING (with timeline)\n")
scheduler = TimelineScheduler(time_quantum=2)
for p in allocated:
    if p.state != ProcessState.TERMINATED:
        p.cpu_time = 0
        p.io_done = False
        scheduler.add_process(p)
scheduler.run()
scheduler.print_timeline()

# ── FAILURE SCENARIO ──────────────────────────────────
print("\n>>> PHASE 5: FAILURE SCENARIO\n")
p6 = PCB(pid=6, name="VideoCapture", priority=2, memory_required=300)
p6.memory_manager = mem
print("[OS] User launched VideoCapture — needs 300MB...")
success = mem.allocate(p6)
if not success:
    mem.handle_exhaustion(p6, allocated)
    mem.allocate(p6)
mem.status()

# ── SHUTDOWN ──────────────────────────────────────────
print("\n>>> PHASE 6: SYSTEM SHUTDOWN\n")
for p in all_processes + [p6]:
    if p.pid in mem.memory_map:
        mem.deallocate(p)
    print(f"[OS] {p.name} — {p.state}")

mem.status()

print("\n" + "=" * 55)
print("     🎮 GAME CONSOLE OS — SHUTDOWN COMPLETE")
print("=" * 55)
print("\nSystems demonstrated:")
print("  ✅ Process creation and PCB design")
print("  ✅ Memory allocation and exhaustion handling")
print("  ✅ Round Robin scheduling with I/O blocking")
print("  ✅ Process execution timeline")
print("  ✅ Controlled failure scenario")
print("  ⏳ File system — Person 3 to implement")
print("  ⏳ Page faults — Person 2 to implement")
print("  ⏳ Deadlock — Person 2 to implement")
print("=" * 55)
