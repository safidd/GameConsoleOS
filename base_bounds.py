from pcb import PCB, ProcessState

class AddressSpace:
    def __init__(self, process, base, size):
        self.process = process
        self.base = base      # where in physical memory this process starts
        self.size = size      # bounds — max allowed virtual address
        print(f"[Memory] {process.name} address space: base={base}KB, size={size}KB")
        print(f"[Memory] Physical range: {base}KB to {base+size}KB")

    def translate(self, virtual_address):
        """Translate virtual address to physical address"""
        if virtual_address < 0 or virtual_address >= self.size:
            print(f"[MMU] SEGFAULT! {self.process.name} accessed virtual address {virtual_address}KB")
            print(f"[MMU] Bounds violation: {virtual_address} >= {self.size} (size)")
            return None
        physical = virtual_address + self.base
        print(f"[MMU] {self.process.name}: virtual {virtual_address}KB -> physical {physical}KB (base={self.base})")
        return physical

class PhysicalMemory:
    def __init__(self, total_kb=64):
        self.total = total_kb
        self.memory = {}      # physical_address -> value
        self.free_list = [(16, total_kb - 16)]  # OS takes first 16KB
        print(f"[Memory] Physical memory: {total_kb}KB total | OS uses 0-16KB")

    def find_free_space(self, size):
        for i, (start, length) in enumerate(self.free_list):
            if length >= size:
                self.free_list[i] = (start + size, length - size)
                return start
        return None

    def write(self, addr, value):
        self.memory[addr] = value

    def read(self, addr):
        return self.memory.get(addr, 0)

    def visualize(self, address_spaces):
        print(f"\n[Memory] Physical memory layout (64KB):")
        print(f"  0KB  - 16KB : Operating System")
        for space in address_spaces:
            end = space.base + space.size
            print(f"  {space.base}KB - {end}KB : {space.process.name} (size={space.size}KB)")
        used = sum(s.size for s in address_spaces) + 16
        print(f"  Used: {used}KB | Free: {self.total - used}KB")

class MMU:
    def __init__(self, physical_memory):
        self.physical_memory = physical_memory
        self.address_spaces = {}  # pid -> AddressSpace

    def register(self, process, size):
        base = self.physical_memory.find_free_space(size)
        if base is None:
            print(f"[MMU] ERROR: No space for {process.name}")
            return None
        space = AddressSpace(process, base, size)
        self.address_spaces[process.pid] = space
        return space

    def load(self, process, virtual_address):
        space = self.address_spaces[process.pid]
        physical = space.translate(virtual_address)
        if physical is None:
            return None
        value = self.physical_memory.read(physical)
        print(f"[MMU] Load: physical[{physical}KB] = {value}")
        return value

    def store(self, process, virtual_address, value):
        space = self.address_spaces[process.pid]
        physical = space.translate(virtual_address)
        if physical is None:
            return False
        self.physical_memory.write(physical, value)
        print(f"[MMU] Store: {value} -> physical[{physical}KB]")
        return True

if __name__ == "__main__":
    print("=" * 55)
    print("     BASE AND BOUNDS ADDRESS TRANSLATION DEMO")
    print("=" * 55)

    mem = PhysicalMemory(total_kb=64)
    mmu = MMU(mem)

    p1 = PCB(pid=1, name="GameProcess",  priority=3, memory_required=16)
    p2 = PCB(pid=2, name="AudioEngine",  priority=3, memory_required=12)
    p3 = PCB(pid=3, name="DownloadMgr",  priority=1, memory_required=8)

    print("\n--- Phase 1: Register processes ---\n")
    mmu.register(p1, size=16)
    mmu.register(p2, size=12)
    mmu.register(p3, size=8)
    mem.visualize(list(mmu.address_spaces.values()))

    print("\n--- Phase 2: Valid address translations ---\n")
    print("[OS] GameProcess stores score=9999 at virtual address 0KB")
    mmu.store(p1, virtual_address=0, value=9999)

    print("\n[OS] GameProcess stores level=5 at virtual address 4KB")
    mmu.store(p1, virtual_address=4, value=5)

    print("\n[OS] AudioEngine stores volume=80 at virtual address 0KB")
    mmu.store(p2, virtual_address=0, value=80)

    print("\n[OS] GameProcess reads score from virtual address 0KB")
    mmu.load(p1, virtual_address=0)

    print("\n[OS] AudioEngine reads volume from virtual address 0KB")
    mmu.load(p2, virtual_address=0)

    print("\n--- Phase 3: Bounds violation ---\n")
    print("[OS] GameProcess tries to access virtual address 20KB (out of bounds!)")
    mmu.load(p1, virtual_address=20)

    print("\n[OS] DownloadMgr tries to access virtual address -1KB (negative!)")
    mmu.load(p3, virtual_address=-1)

    print("\n--- Phase 4: Process isolation ---\n")
    print("[OS] AudioEngine tries to read GameProcess virtual address 0KB")
    print("[OS] AudioEngine gets ITS OWN physical memory, not GameProcess's!")
    val = mmu.load(p2, virtual_address=0)
    print(f"[OS] AudioEngine reads {val} — completely isolated from GameProcess\n")

    print("=" * 55)
    print("CONCLUSION:")
    print("Virtual address + base = physical address")
    print("Bounds register prevents illegal access")
    print("Each process is fully isolated in memory")
    print("=" * 55)