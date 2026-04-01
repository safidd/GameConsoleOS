from pcb import PCB, ProcessState
from rr_scheduler import RoundRobinScheduler
from memory_manager import MemoryManager
from file_system import FileSystem, SaveBuffer
from page_fault import PageTable
from deadlock import DeadlockDetector, Resource
from timeline import TimelineScheduler

print("\n" + "=" * 55)
print("     🎮 GAME CONSOLE OS — FULL SIMULATION")
print("=" * 55)

# ── BOOT ──────────────────────────────────────────────
print("\n>>> PHASE 1: SYSTEM BOOT\n")
mem      = MemoryManager(total_memory=512)
fs       = FileSystem()
pt       = PageTable(total_frames=8)
pt.frames     = {0: 0, 1: 1, 2: 2}
pt.free_frames = [3, 4, 5, 6, 7]
print("[OS] Memory Manager online — 512MB RAM")
print("[OS] File System online")
print("[OS] Page Table online — 8 frames (3 pre-loaded)")

# ── PROCESSES ─────────────────────────────────────────
print("\n>>> PHASE 2: PROCESS CREATION\n")
p1 = PCB(pid=1, name="GameProcess",    priority=3, memory_required=256)
p2 = PCB(pid=2, name="DownloadMgr",    priority=1, memory_required=80)
p3 = PCB(pid=3, name="SaveThread",     priority=2, memory_required=40)
p4 = PCB(pid=4, name="AudioEngine",    priority=3, memory_required=60)
p5 = PCB(pid=5, name="CloudBackup",    priority=1, memory_required=70)

for p in [p1,p2,p3,p4,p5]:
    p.memory_manager = mem
    p.io_done = False

p1.burst_time = 5; p1.is_io_bound = False; p1.pages = [0,1,5]
p2.burst_time = 3; p2.is_io_bound = False; p2.pages = [1,2,6]
p3.burst_time = 4; p3.is_io_bound = True;  p3.pages = [0,3]
p4.burst_time = 3; p4.is_io_bound = False; p4.pages = [2,4]
p5.burst_time = 3; p5.is_io_bound = False; p5.pages = [1,7]

all_processes = [p1,p2,p3,p4,p5]
for p in all_processes:
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

# ── FILE SYSTEM ───────────────────────────────────────
print("\n>>> PHASE 4: FILE SYSTEM SETUP\n")
fs.create("savegame.dat", p1)
fs.create("audio.cfg",    p4)
fs.write("savegame.dat", "level=1,score=0", p1)
fs.write("audio.cfg",    "volume=80",       p4)
buf = SaveBuffer(fs)
fs.create("autosave.dat", p3)
buf.produce("checkpoint_start", p1)
buf.consume(p3, "autosave.dat")
fs.list_files()

# ── PAGE FAULTS ───────────────────────────────────────
print("\n>>> PHASE 5: PAGE FAULT SIMULATION\n")
for p in [p1,p2,p3,p4,p5]:
    print(f"[Memory] Checking pages for {p.name}...")
    for page in p.pages:
        pt.access_page(p, page)
print(f"\n[Memory] Total page faults: {pt.fault_count}")

# ── SCHEDULING + TIMELINE ────────────────────────────
print("\n>>> PHASE 6: SCHEDULING (with timeline)\n")
scheduler = TimelineScheduler(time_quantum=2)
for p in allocated:
    if p.state != ProcessState.TERMINATED:
        p.cpu_time = 0
        p.io_done = False
        scheduler.add_process(p)
scheduler.run()
scheduler.print_timeline()

# ── DEADLOCK ──────────────────────────────────────────
print("\n>>> PHASE 7: DEADLOCK SCENARIO\n")
detector    = DeadlockDetector()
save_lock   = Resource("save_lock")
net_lock    = Resource("net_lock")
detector.add_resource(save_lock)
detector.add_resource(net_lock)

px = PCB(pid=10, name="GameProcess",  priority=3, memory_required=256)
py = PCB(pid=11, name="CloudBackup",  priority=1, memory_required=70)
detector.add_process(px)
detector.add_process(py)

detector.acquire(px, save_lock)
detector.acquire(py, net_lock)
detector.acquire(px, net_lock)
detector.acquire(py, save_lock)

if detector.detect_deadlock():
    detector.resolve_deadlock()
    detector.detect_deadlock()

# ── FAILURE SCENARIO ──────────────────────────────────
print("\n>>> PHASE 8: FAILURE SCENARIO\n")
p6 = PCB(pid=6, name="VideoCapture", priority=2, memory_required=300)
p6.memory_manager = mem
print("[OS] User launched VideoCapture — needs 300MB...")
success = mem.allocate(p6)
if not success:
    mem.handle_exhaustion(p6, allocated)
    mem.allocate(p6)
mem.status()

# ── SHUTDOWN ──────────────────────────────────────────
print("\n>>> PHASE 9: SYSTEM SHUTDOWN\n")
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
print("  ✅ File system with producer-consumer")
print("  ✅ Page fault detection and frame eviction")
print("  ✅ Round Robin scheduling with I/O blocking")
print("  ✅ Process execution timeline")
print("  ✅ Deadlock detection and resolution")
print("  ✅ Controlled failure scenario")
print("=" * 55)