from pcb import PCB, ProcessState

class Segment:
    def __init__(self, name, base, size, grows_negative=False):
        self.name = name
        self.base = base
        self.size = size
        self.grows_negative = grows_negative  # True for stack

    def __repr__(self):
        direction = "↓" if self.grows_negative else "↑"
        return f"[{self.name}: base={self.base}KB size={self.size}KB {direction}]"

class SegmentationMMU:
    def __init__(self):
        self.segments = {}   # process_pid -> {seg_name -> Segment}

    def register(self, process, code_base, code_size,
                 heap_base, heap_size,
                 stack_base, stack_size):
        self.segments[process.pid] = {
            "code":  Segment("code",  code_base,  code_size),
            "heap":  Segment("heap",  heap_base,  heap_size),
            "stack": Segment("stack", stack_base, stack_size, grows_negative=True),
        }
        print(f"[Seg] {process.name} segments registered:")
        for s in self.segments[process.pid].values():
            print(f"  {s}")

    def translate(self, process, virtual_address, segment_name):
        segs = self.segments.get(process.pid)
        if not segs or segment_name not in segs:
            print(f"[Seg] ERROR: Unknown segment '{segment_name}'")
            return None

        seg = segs[segment_name]

        if seg.grows_negative:
            # stack grows downward
            physical = seg.base - virtual_address
            if virtual_address > seg.size:
                print(f"[Seg] SEGFAULT! {process.name} stack overflow at virtual -{virtual_address}KB")
                return None
            print(f"[Seg] {process.name} [{segment_name}] virtual -{virtual_address}KB -> physical {physical}KB")
        else:
            # code and heap grow upward
            if virtual_address >= seg.size:
                print(f"[Seg] SEGFAULT! {process.name} [{segment_name}] virtual {virtual_address}KB out of bounds (size={seg.size}KB)")
                return None
            physical = seg.base + virtual_address
            print(f"[Seg] {process.name} [{segment_name}] virtual {virtual_address}KB -> physical {physical}KB")

        return physical

    def visualize(self, processes):
        print(f"\n[Seg] Physical memory layout:")
        print(f"  0KB  - 16KB : Operating System")
        all_segs = []
        for pid, segs in self.segments.items():
            for seg in segs.values():
                all_segs.append(seg)
        all_segs.sort(key=lambda s: s.base)
        for s in all_segs:
            end = s.base + s.size
            direction = "(grows down)" if s.grows_negative else ""
            print(f"  {s.base}KB - {end}KB : {s.name} {direction}")
        print()

if __name__ == "__main__":
    print("=" * 55)
    print("     SEGMENTATION DEMO")
    print("=" * 55)

    mmu = SegmentationMMU()

    p1 = PCB(pid=1, name="GameProcess", priority=3, memory_required=0)
    p2 = PCB(pid=2, name="AudioEngine", priority=3, memory_required=0)

    print("\n--- Phase 1: Register process segments ---\n")
    # GameProcess: code at 16KB, heap at 24KB, stack top at 48KB
    mmu.register(p1,
        code_base=16,  code_size=4,
        heap_base=24,  heap_size=8,
        stack_base=48, stack_size=4
    )

    # AudioEngine: code at 20KB, heap at 32KB, stack top at 52KB
    mmu.register(p2,
        code_base=20,  code_size=4,
        heap_base=32,  heap_size=6,
        stack_base=52, stack_size=4
    )

    mmu.visualize([p1, p2])

    print("--- Phase 2: Valid translations ---\n")
    print("[OS] GameProcess accesses code at virtual 0KB:")
    mmu.translate(p1, 0, "code")

    print("\n[OS] GameProcess accesses heap at virtual 2KB:")
    mmu.translate(p1, 2, "heap")

    print("\n[OS] GameProcess accesses stack at virtual 2KB (grows down):")
    mmu.translate(p1, 2, "stack")

    print("\n[OS] AudioEngine accesses code at virtual 1KB:")
    mmu.translate(p2, 1, "code")

    print("\n--- Phase 3: Bounds violations ---\n")
    print("[OS] GameProcess tries to access code at virtual 10KB (too big):")
    mmu.translate(p1, 10, "code")

    print("\n[OS] GameProcess stack overflow (virtual 8KB > stack size 4KB):")
    mmu.translate(p1, 8, "stack")

    print("\n--- Phase 4: Why segmentation is better than base/bounds ---\n")
    print("[Seg] With base/bounds: the WHOLE address space is allocated")
    print("[Seg] including the free space between heap and stack")
    print("[Seg] With segmentation: only code, heap, stack are allocated")
    print("[Seg] The free space between heap and stack is NOT wasted!\n")

    code_size  = 4
    heap_size  = 8
    stack_size = 4
    total_seg  = code_size + heap_size + stack_size
    total_bb   = 48 - 16  # full address space from base/bounds example
    print(f"[Seg] Base/bounds would allocate: {total_bb}KB for GameProcess")
    print(f"[Seg] Segmentation allocates:     {total_seg}KB for GameProcess")
    print(f"[Seg] Memory saved:               {total_bb - total_seg}KB")

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("Segmentation gives each segment (code, heap, stack)")
    print("its own base and bounds register.")
    print("Free space between segments is NOT allocated.")
    print("More efficient than base/bounds but can cause")
    print("external fragmentation over time.")
    print("=" * 55)