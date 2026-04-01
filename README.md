# 🎮 Game Console OS — Mini Operating System Simulator

A Python-based mini OS simulation built for the Operating Systems course at Acıbadem University.

## 📌 Overview

This project simulates a fictional game console OS with four core subsystems:
- **Process Management** — PCB design, process states, creation and termination
- **CPU Scheduling** — FIFO (baseline) and Round Robin (enhanced)
- **Memory Management** — Allocation, deallocation, and exhaustion handling
- **File System Interaction** — I/O blocking and cross-component interaction

## 🗂️ Project Structure

| File | Description |
|---|---|
| `pcb.py` | Process Control Block — blueprint for every process |
| `scheduler.py` | FIFO baseline scheduler |
| `rr_scheduler.py` | Round Robin scheduler with I/O blocking |
| `memory_manager.py` | Memory allocator with exhaustion handling |
| `main.py` | Full simulation — runs all subsystems together |
| `starvation_demo.py` | Demonstrates starvation in FIFO vs Round Robin |

## 🚀 How to Run

Make sure you have Python 3 installed.

**Run the full simulation:**
```bash
python3 main.py
```

**Run the starvation demo:**
```bash
python3 starvation_demo.py
```

**Run individual components:**
```bash
python3 scheduler.py
python3 rr_scheduler.py
python3 memory_manager.py
```

## 🔄 Simulation Phases

**Phase 1 — Memory Allocation**
Three processes (GameProcess, DownloadManager, SaveThread) are loaded into 512MB RAM.

**Phase 2 — Scheduling**
Round Robin scheduler runs all processes with a time quantum of 2 units.
SaveThread triggers a file I/O event and gets BLOCKED — scheduler moves to next process.
Memory is automatically freed when each process terminates.

**Phase 3 — Failure Scenario**
ScreenshotService attempts to launch when memory is nearly full.
Memory exhaustion handler kills lowest priority processes until enough memory is freed.

## ⚙️ Design Decisions

| Component | Choice | Alternative | Reason |
|---|---|---|---|
| Scheduler | Round Robin | FIFO / MLFQ | Fairness over throughput |
| Memory eviction | Priority-based | LRU / Random | Predictable behavior |
| I/O handling | BLOCKED state | Busy waiting | CPU efficiency |

## 🎮 Theme

Processes represent real game console tasks:
- **GameProcess** (priority 3) — the active game, always highest priority
- **DownloadManager** (priority 1) — background download
- **SaveThread** (priority 2) — saves game data, triggers file I/O
- **ScreenshotService** (priority 1) — background screenshot capture

## 👥 Team: Safiye Demirkıran, Fatıma Betül Zorlu, Mina Narman
