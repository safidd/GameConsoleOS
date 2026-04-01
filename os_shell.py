from pcb import PCB, ProcessState
from rr_scheduler import RoundRobinScheduler
from memory_manager import MemoryManager
from file_system import FileSystem

class GameConsoleShell:
    def __init__(self):
        self.mem       = MemoryManager(total_memory=512)
        self.scheduler = RoundRobinScheduler(time_quantum=2)
        self.fs        = FileSystem()
        self.processes = {}
        self.next_pid  = 1
        self.running   = True

        self.commands = {
            "help":    self.cmd_help,
            "launch":  self.cmd_launch,
            "kill":    self.cmd_kill,
            "ps":      self.cmd_ps,
            "mem":     self.cmd_mem,
            "run":     self.cmd_run,
            "mkfile":  self.cmd_mkfile,
            "write":   self.cmd_write,
            "read":    self.cmd_read,
            "ls":      self.cmd_ls,
            "clear":   self.cmd_clear,
            "exit":    self.cmd_exit,
        }

        self.process_templates = {
            "game":       ("GameProcess",    3, 256, 6),
            "download":   ("DownloadMgr",    1, 80,  4),
            "save":       ("SaveThread",     2, 40,  4),
            "audio":      ("AudioEngine",    3, 60,  3),
            "screenshot": ("ScreenshotSvc",  1, 30,  2),
            "video":      ("VideoCapture",   2, 90,  5),
            "cloud":      ("CloudBackup",    1, 70,  3),
        }

    def boot(self):
        print("\n" + "=" * 55)
        print("     🎮 GAME CONSOLE OS — INTERACTIVE SHELL")
        print("=" * 55)
        print("  Type 'help' to see available commands")
        print("  Type 'exit' to shutdown")
        print("=" * 55 + "\n")

    def cmd_help(self, args):
        print("\n  Available commands:")
        print("  launch <name>     — launch a process (game, download, save,")
        print("                      audio, screenshot, video, cloud)")
        print("  kill <pid>        — kill a process by PID")
        print("  ps                — list all processes")
        print("  mem               — show memory status")
        print("  run               — run scheduler for one cycle")
        print("  mkfile <name>     — create a file")
        print("  write <name> <data> — write data to a file")
        print("  read <name>       — read a file")
        print("  ls                — list all files")
        print("  clear             — clear screen")
        print("  exit              — shutdown OS\n")

    def cmd_launch(self, args):
        if not args:
            print("  Usage: launch <name>")
            print("  Options:", ", ".join(self.process_templates.keys()))
            return
        name = args[0].lower()
        if name not in self.process_templates:
            print(f"  Unknown process '{name}'. Options: {', '.join(self.process_templates.keys())}")
            return
        pname, priority, mem_req, burst = self.process_templates[name]
        p = PCB(pid=self.next_pid, name=pname, priority=priority, memory_required=mem_req)
        p.burst_time = burst
        p.cpu_time = 0
        p.io_done = False
        p.is_io_bound = name == "save"
        p.memory_manager = self.mem
        self.next_pid += 1
        success = self.mem.allocate(p)
        if not success:
            print(f"  Not enough memory — attempting exhaustion handling...")
            self.mem.handle_exhaustion(p, list(self.processes.values()))
            success = self.mem.allocate(p)
        if success:
            self.processes[p.pid] = p
            self.scheduler.add_process(p)
            print(f"  Launched {pname} (PID:{p.pid}) priority={priority} memory={mem_req}MB")
        else:
            print(f"  Failed to launch {pname} — not enough memory")

    def cmd_kill(self, args):
        if not args:
            print("  Usage: kill <pid>")
            return
        try:
            pid = int(args[0])
        except ValueError:
            print("  PID must be a number")
            return
        if pid not in self.processes:
            print(f"  No process with PID {pid}")
            return
        p = self.processes[pid]
        p.state = ProcessState.TERMINATED
        self.mem.deallocate(p)
        print(f"  Killed {p.name} (PID:{pid})")

    def cmd_ps(self, args):
        if not self.processes:
            print("  No processes running.")
            return
        print(f"\n  {'PID':>4}  {'Name':<18} {'State':<12} {'Priority':>8} {'Memory':>8} {'CPU':>8}")
        print(f"  {'---':>4}  {'----':<18} {'-----':<12} {'--------':>8} {'------':>8} {'---':>8}")
        for p in self.processes.values():
            cpu = f"{p.cpu_time}/{p.burst_time}"
            print(f"  {p.pid:>4}  {p.name:<18} {p.state:<12} {p.priority:>8} {p.memory_required:>7}MB {cpu:>8}")
        print()

    def cmd_mem(self, args):
        self.mem.status()

    def cmd_run(self, args):
        active = [p for p in self.processes.values() if p.state != ProcessState.TERMINATED]
        if not active:
            print("  No active processes to run.")
            return
        print(f"  Running scheduler for one cycle...\n")
        self.scheduler.run()

    def cmd_mkfile(self, args):
        if not args:
            print("  Usage: mkfile <filename>")
            return
        dummy = PCB(pid=0, name="Shell", priority=1, memory_required=0)
        self.fs.create(args[0], dummy)

    def cmd_write(self, args):
        if len(args) < 2:
            print("  Usage: write <filename> <data>")
            return
        dummy = PCB(pid=0, name="Shell", priority=1, memory_required=0)
        self.fs.write(args[0], " ".join(args[1:]), dummy)

    def cmd_read(self, args):
        if not args:
            print("  Usage: read <filename>")
            return
        dummy = PCB(pid=0, name="Shell", priority=1, memory_required=0)
        self.fs.read(args[0], dummy)

    def cmd_ls(self, args):
        self.fs.list_files()

    def cmd_clear(self, args):
        import os
        os.system("clear")

    def cmd_exit(self, args):
        print("\n  Shutting down Game Console OS...")
        for p in self.processes.values():
            if p.pid in self.mem.memory_map:
                self.mem.deallocate(p)
        print("  All processes terminated. Goodbye!\n")
        self.running = False

    def run(self):
        self.boot()
        while self.running:
            try:
                user_input = input("  console> ").strip()
                if not user_input:
                    continue
                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"  Unknown command '{cmd}'. Type 'help' for commands.")
            except KeyboardInterrupt:
                print("\n  Use 'exit' to shutdown.")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    shell = GameConsoleShell()
    shell.run()