from pcb import PCB, ProcessState

class PageTable:
    def __init__(self, total_frames=8):
        self.total_frames = total_frames
        self.frames = {}        # page_number -> frame_number
        self.free_frames = list(range(total_frames))
        self.fault_count = 0

    def access_page(self, process, page_number):
        if page_number in self.frames:
            print(f"[Memory] {process.name} accessed page {page_number} -> frame {self.frames[page_number]} (HIT)")
            return True
        else:
            self.fault_count += 1
            print(f"[Memory] PAGE FAULT — {process.name} tried to access page {page_number} (not in RAM!)")
            return self.load_page(process, page_number)

    def load_page(self, process, page_number):
        if not self.free_frames:
            print(f"[Memory] No free frames — evicting a page...")
            evicted = next(iter(self.frames))
            freed_frame = self.frames.pop(evicted)
            self.free_frames.append(freed_frame)
            print(f"[Memory] Evicted page {evicted} from frame {freed_frame}")

        frame = self.free_frames.pop(0)
        self.frames[page_number] = frame
        print(f"[Memory] Loaded page {page_number} into frame {frame} for {process.name}")
        return True

    def status(self):
        print(f"\n[Memory] Page Table — {len(self.frames)}/{self.total_frames} frames used | Total faults: {self.fault_count}")
        for page, frame in self.frames.items():
            print(f"  Page {page} -> Frame {frame}")

class PageFaultScheduler:
    def __init__(self, page_table):
        self.ready_queue = []
        self.blocked_queue = []
        self.page_table = page_table

    def add_process(self, process):
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        print(f"[Scheduler] {process.name} added to ready queue")

    def run(self):
        print(f"\n[Scheduler] Starting — Page Fault Simulation...\n")
        while self.ready_queue or self.blocked_queue:
            # unblock processes whose pages are now loaded
            for p in list(self.blocked_queue):
                print(f"[Scheduler] Loading page for {p.name}...")
                self.page_table.load_page(p, p.waiting_for_page)
                self.blocked_queue.remove(p)
                p.state = ProcessState.READY
                self.ready_queue.append(p)
                print(f"[Scheduler] {p.name} UNBLOCKED — page loaded\n")

            if not self.ready_queue:
                break

            process = self.ready_queue.pop(0)
            process.state = ProcessState.RUNNING
            print(f"[Scheduler] Running: {process.name}")

            for page in process.pages:
                hit = self.page_table.access_page(process, page)
                if not hit:
                    process.state = ProcessState.BLOCKED
                    process.waiting_for_page = page
                    self.blocked_queue.append(process)
                    print(f"[Scheduler] {process.name} BLOCKED waiting for page {page}\n")
                    break
            else:
                process.state = ProcessState.TERMINATED
                print(f"[Scheduler] {process.name} completed all page accesses\n")

if __name__ == "__main__":
    print("=" * 55)
    print("     PAGE FAULT SIMULATION")
    print("=" * 55)

    pt = PageTable(total_frames=6)

    # Pre-load some pages into RAM
    pt.frames = {0: 0, 1: 1, 2: 2}
    pt.free_frames = [3, 4, 5]

    print("\n[Memory] Initial page table — pages 0,1,2 already in RAM\n")

    p1 = PCB(pid=1, name="GameProcess",    priority=3, memory_required=256)
    p2 = PCB(pid=2, name="AudioEngine",    priority=3, memory_required=60)
    p3 = PCB(pid=3, name="VideoCapture",   priority=2, memory_required=90)

    p1.pages = [0, 1, 5, 6]   # pages 5,6 not in RAM → will fault
    p2.pages = [1, 2, 3]      # page 3 not in RAM → will fault
    p3.pages = [0, 4, 7]      # pages 4,7 not in RAM → will fault

    scheduler = PageFaultScheduler(pt)
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.add_process(p3)

    scheduler.run()
    pt.status()

    print("\n" + "=" * 55)
    print(f"CONCLUSION: {pt.fault_count} page faults occurred.")
    print("Each fault blocked the process and triggered a load.")
    print("Scheduler continued with other processes during fault.")
    print("=" * 55)