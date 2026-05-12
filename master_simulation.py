from pcb import PCB, ProcessState
from rr_scheduler import RoundRobinScheduler
from memory_manager import MemoryManager
from timeline import TimelineScheduler
from file_system import FileSystem
from concurrency import SaveGameBuffer
import threading

print("\n" + "=" * 55)
print("     🎮 GAME CONSOLE OS — FULL SIMULATION")
print("=" * 55)

# ── BOOT ──────────────────────────────────────────────
print("\n>>> PHASE 1: SYSTEM BOOT\n")
mem = MemoryManager(total_memory=512)
fs  = FileSystem()
print("[OS] Memory Manager online — 512MB RAM")
print("[OS] File System online")
print("[OS] Scheduler online")

# ── PROCESSES ─────────────────────────────────────────
print("\n>>> PHASE 2: PROCESS CREATION\n")
p1 = PCB(pid=1, name="GameProcess",  priority=3, memory_required=256)
p2 = PCB(pid=2, name="DownloadMgr",  priority=1, memory_required=80)
p3 = PCB(pid=3, name="SaveThread",   priority=2, memory_required=40)
p4 = PCB(pid=4, name="AudioEngine",  priority=3, memory_required=60)
p5 = PCB(pid=5, name="CloudBackup",  priority=1, memory_required=70)

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

# ── FILE SYSTEM & CONCURRENCY ─────────────────────────
print("\n>>> PHASE 5: FILE SYSTEM & CONCURRENCY\n")
fs.create_file("/saves", "savegame.dat", "level=1,score=0")
fs.create_file("/games", "game.cfg",     "resolution=1080p")
fs.create_file("/system", "boot.cfg",   "quantum=2,ram=512")

print("\n[OS] SaveThread writes save file — gets BLOCKED during I/O...\n")
fs.write_file("/saves", "savegame.dat", "level=5,score=9999", process=p3)

print()
fs.read_file("/saves", "savegame.dat")
fs.list_files()

print("[Concurrency] Testing producer-consumer save buffer...\n")
buf = SaveGameBuffer(capacity=3)

def producer():
    for item in ["checkpoint_1", "checkpoint_2", "checkpoint_3"]:
        buf.produce(item)

def consumer():
    for _ in range(3):
        buf.consume()

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()

# ── FAILURE SCENARIO ──────────────────────────────────
print("\n>>> PHASE 6: FAILURE SCENARIO\n")
p6 = PCB(pid=6, name="VideoCapture", priority=2, memory_required=300)
p6.memory_manager = mem
print("[OS] User launched VideoCapture — needs 300MB...")
success = mem.allocate(p6)
if not success:
    mem.handle_exhaustion(p6, allocated)
    mem.allocate(p6)
mem.status()

# ── SHUTDOWN ──────────────────────────────────────────
print("\n>>> PHASE 7: SYSTEM SHUTDOWN\n")
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
print("  ✅ File system with directory structure")
print("  ✅ Concurrency — producer-consumer save buffer")
print("  ✅ Controlled failure scenario")
print("=" * 55)