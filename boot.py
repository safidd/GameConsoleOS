import time
import os

def clear():
    os.system("clear")

def slow_print(text, delay=0.03):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def progress_bar(label, steps=20, delay=0.05):
    print(f"  {label:<30} [", end="", flush=True)
    for i in range(steps):
        time.sleep(delay)
        print("█", end="", flush=True)
    print("] OK")

def boot():
    clear()
    time.sleep(0.3)

    # Logo
    print("\n")
    slow_print("  ██████╗  █████╗ ███╗   ███╗███████╗", 0.01)
    slow_print("  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝", 0.01)
    slow_print("  ██║  ███╗███████║██╔████╔██║█████╗  ", 0.01)
    slow_print("  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ", 0.01)
    slow_print("  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗", 0.01)
    slow_print("   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝", 0.01)
    print()
    slow_print("         🎮 GAME CONSOLE OS v1.0", 0.02)
    slow_print("      Acıbadem University — OS Project", 0.02)
    print()
    time.sleep(0.5)

    # BIOS info
    slow_print("  BIOS Version 1.0.0", 0.02)
    slow_print("  CPU: GameCore X1 @ 3.5GHz", 0.02)
    slow_print("  RAM: 512MB detected", 0.02)
    slow_print("  Storage: 64GB internal", 0.02)
    print()
    time.sleep(0.3)

    # Boot sequence
    slow_print("  Starting Game Console OS...\n", 0.03)
    time.sleep(0.2)

    progress_bar("Loading kernel",          steps=15, delay=0.04)
    progress_bar("Initializing memory",     steps=15, delay=0.03)
    progress_bar("Starting scheduler",      steps=15, delay=0.03)
    progress_bar("Mounting file system",    steps=15, delay=0.04)
    progress_bar("Loading device drivers",  steps=15, delay=0.03)
    progress_bar("Starting audio engine",   steps=15, delay=0.02)
    progress_bar("Starting network stack",  steps=15, delay=0.04)
    progress_bar("Loading user profile",    steps=15, delay=0.03)
    print()
    time.sleep(0.3)

    slow_print("  ✅ All systems online.", 0.03)
    time.sleep(0.2)
    slow_print("  ✅ Memory manager ready.", 0.03)
    time.sleep(0.2)
    slow_print("  ✅ Scheduler ready.", 0.03)
    time.sleep(0.2)
    slow_print("  ✅ File system mounted.", 0.03)
    time.sleep(0.2)
    slow_print("  ✅ Network online.", 0.03)
    time.sleep(0.4)
    print()
    slow_print("  🎮 Welcome to Game Console OS!", 0.04)
    time.sleep(0.3)
    print()

    # ask to launch shell
    slow_print("  Press ENTER to launch the shell...", 0.02)
    input()

    # launch shell
    from os_shell import GameConsoleShell
    shell = GameConsoleShell()
    shell.run()

if __name__ == "__main__":
    boot()