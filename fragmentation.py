from pcb import PCB, ProcessState

class FragmentedMemory:
    def __init__(self, total_memory=512):
        self.total_memory = total_memory
        # memory is a list of blocks: {"start", "size", "pid", "free"}
        self.blocks = [{"start": 0, "size": total_memory, "pid": None, "free": True}]

    def allocate(self, process):
        for block in self.blocks:
            if block["free"] and block["size"] >= process.memory_required:
                # split block
                remaining = block["size"] - process.memory_required
                block["free"] = False
                block["pid"] = process.pid
                block["name"] = process.name
                block["size"] = process.memory_required
                if remaining > 0:
                    new_block = {
                        "start": block["start"] + process.memory_required,
                        "size": remaining,
                        "pid": None,
                        "free": True
                    }
                    self.blocks.insert(self.blocks.index(block) + 1, new_block)
                print(f"[Memory] Allocated {process.memory_required}MB to {process.name} at offset {block['start']}")
                return True
        print(f"[Memory] FAILED: Not enough contiguous memory for {process.name} ({process.memory_required}MB)")
        return False

    def deallocate(self, process):
        for block in self.blocks:
            if not block["free"] and block["pid"] == process.pid:
                block["free"] = True
                block["pid"] = None
                block["name"] = None
                print(f"[Memory] Freed {block['size']}MB at offset {block['start']} (was {process.name})")
                self.merge_free_blocks()
                return

    def merge_free_blocks(self):
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i]["free"] and self.blocks[i+1]["free"]:
                self.blocks[i]["size"] += self.blocks[i+1]["size"]
                self.blocks.pop(i+1)
            else:
                i += 1

    def compact(self):
        print(f"\n[Memory] Running compaction — moving all used blocks together...")
        used = [b for b in self.blocks if not b["free"]]
        free_total = sum(b["size"] for b in self.blocks if b["free"])
        new_blocks = []
        offset = 0
        for b in used:
            new_b = dict(b)
            new_b["start"] = offset
            offset += b["size"]
            new_blocks.append(new_b)
            print(f"[Memory] Moved {b['name']} to offset {new_b['start']}")
        if free_total > 0:
            new_blocks.append({"start": offset, "size": free_total, "pid": None, "free": True})
        self.blocks = new_blocks
        print(f"[Memory] Compaction done — {free_total}MB free space consolidated at end")

    def largest_free_block(self):
        free = [b["size"] for b in self.blocks if b["free"]]
        return max(free) if free else 0

    def total_free(self):
        return sum(b["size"] for b in self.blocks if b["free"])

    def visualize(self):
        print(f"\n[Memory] Layout (total={self.total_memory}MB):")
        bar = ""
        for b in self.blocks:
            width = max(1, b["size"] // 8)
            if b["free"]:
                bar += "░" * width
            else:
                bar += "█" * width
        print(f"  |{bar}|")
        print(f"  0" + " " * (len(bar)-2) + f"{self.total_memory}MB")
        print(f"\n  Blocks:")
        for b in self.blocks:
            status = "FREE" if b["free"] else b.get("name", "USED")
            print(f"    offset={b['start']:>4}MB  size={b['size']:>4}MB  [{status}]")
        print(f"\n  Total free: {self.total_free()}MB | Largest contiguous: {self.largest_free_block()}MB")

if __name__ == "__main__":
    print("=" * 55)
    print("     MEMORY FRAGMENTATION DEMO")
    print("=" * 55)

    mem = FragmentedMemory(total_memory=512)

    p1 = PCB(pid=1, name="GameProcess",   priority=3, memory_required=150)
    p2 = PCB(pid=2, name="DownloadMgr",   priority=1, memory_required=80)
    p3 = PCB(pid=3, name="SaveThread",    priority=2, memory_required=60)
    p4 = PCB(pid=4, name="AudioEngine",   priority=3, memory_required=100)
    p5 = PCB(pid=5, name="VideoCapture",  priority=2, memory_required=120)

    print("\n--- Phase 1: Allocate 4 processes ---\n")
    mem.allocate(p1)
    mem.allocate(p2)
    mem.allocate(p3)
    mem.allocate(p4)
    mem.visualize()

    print("\n--- Phase 2: Free middle processes (fragmentation occurs) ---\n")
    mem.deallocate(p2)
    mem.deallocate(p3)
    mem.visualize()

    print("\n--- Phase 3: Try to allocate VideoCapture (120MB) ---\n")
    print(f"[Memory] VideoCapture needs 120MB")
    print(f"[Memory] Total free: {mem.total_free()}MB | Largest contiguous: {mem.largest_free_block()}MB")
    success = mem.allocate(p5)
    if not success:
        print(f"[Memory] Fragmentation prevents allocation even though enough total free memory exists!")

    print("\n--- Phase 4: Compaction ---\n")
    mem.compact()
    mem.visualize()

    print("\n--- Phase 5: Retry allocation after compaction ---\n")
    success = mem.allocate(p5)
    if success:
        print(f"[Memory] VideoCapture allocated successfully after compaction!")
    mem.visualize()

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("Fragmentation: total free memory is enough but")
    print("no single contiguous block is large enough.")
    print("Compaction: moves all used blocks together,")
    print("creating one large free block at the end.")
    print("=" * 55)