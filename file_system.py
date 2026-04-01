import time

class File:
    def __init__(self, name):
        self.name = name
        self.content = ""
        self.created_at = time.time()
        self.locked_by = None

    def __repr__(self):
        return f"[File: {self.name} | size: {len(self.content)} chars]"

class FileSystem:
    def __init__(self):
        self.files = {}

    def create(self, name, process):
        if name in self.files:
            print(f"[FS] ERROR: {name} already exists")
            return False
        self.files[name] = File(name)
        print(f"[FS] {process.name} created file '{name}'")
        return True

    def write(self, name, content, process):
        if name not in self.files:
            print(f"[FS] ERROR: {name} does not exist")
            return False
        f = self.files[name]
        if f.locked_by and f.locked_by != process:
            print(f"[FS] {process.name} BLOCKED — '{name}' locked by {f.locked_by.name}")
            return False
        f.locked_by = process
        f.content += content
        print(f"[FS] {process.name} wrote to '{name}': \"{content}\"")
        f.locked_by = None
        return True

    def read(self, name, process):
        if name not in self.files:
            print(f"[FS] ERROR: {name} does not exist")
            return None
        print(f"[FS] {process.name} read '{name}': \"{self.files[name].content}\"")
        return self.files[name].content

    def delete(self, name, process):
        if name not in self.files:
            print(f"[FS] ERROR: {name} does not exist")
            return False
        del self.files[name]
        print(f"[FS] {process.name} deleted '{name}'")
        return True

    def list_files(self):
        print(f"\n[FS] Directory listing ({len(self.files)} files):")
        for f in self.files.values():
            print(f"  {f}")

import threading
import queue

class SaveBuffer:
    """Producer-consumer buffer between GameProcess and SaveThread"""
    def __init__(self, fs):
        self.buffer = queue.Queue(maxsize=5)
        self.fs = fs
        self.lock = threading.Lock()

    def produce(self, data, process):
        try:
            self.buffer.put_nowait(data)
            print(f"[Buffer] {process.name} added save data: '{data}' | Buffer size: {self.buffer.qsize()}")
        except queue.Full:
            print(f"[Buffer] {process.name} BLOCKED — buffer full!")

    def consume(self, process, filename):
        if not self.buffer.empty():
            with self.lock:
                data = self.buffer.get()
                print(f"[Buffer] {process.name} consumed: '{data}' — writing to disk...")
                self.fs.write(filename, data + " ", process)
        else:
            print(f"[Buffer] {process.name} — buffer empty, nothing to save")

if __name__ == "__main__":
    from pcb import PCB

    print("=" * 55)
    print("     FILE SYSTEM + PRODUCER-CONSUMER DEMO")
    print("=" * 55)

    fs = FileSystem()
    game   = PCB(pid=1, name="GameProcess", priority=3, memory_required=256)
    saver  = PCB(pid=3, name="SaveThread",  priority=2, memory_required=64)
    viewer = PCB(pid=4, name="MenuProcess", priority=2, memory_required=32)

    print("\n--- File System Operations ---\n")
    fs.create("savegame.dat", game)
    fs.create("settings.cfg", game)
    fs.write("savegame.dat", "level=5,score=1200", game)
    fs.write("settings.cfg", "volume=80,brightness=70", game)
    fs.read("savegame.dat", viewer)
    fs.list_files()

    print("\n--- Producer-Consumer (Save Buffer) ---\n")
    buf = SaveBuffer(fs)
    fs.create("autosave.dat", saver)

    buf.produce("checkpoint_1", game)
    buf.produce("checkpoint_2", game)
    buf.produce("checkpoint_3", game)

    buf.consume(saver, "autosave.dat")
    buf.consume(saver, "autosave.dat")
    buf.consume(saver, "autosave.dat")
    buf.consume(saver, "autosave.dat")

    fs.read("autosave.dat", viewer)
    fs.list_files()

    print("\n--- File Deletion ---\n")
    fs.delete("settings.cfg", game)
    fs.list_files()

    print("\n" + "=" * 55)
    print("File system and producer-consumer working!")
    print("=" * 55)