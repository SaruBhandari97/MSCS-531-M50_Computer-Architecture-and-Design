# Assignment 3 — Exploring Memory Hierarchy Design in gem5 (x86)

**Student:** Saru Bhandari  
**Course:** Computer Architecture / gem5 Laboratory  
**Assignment:** Memory Hierarchy Design (Part 1 + Part 2)  
**Simulator:** gem5 25.1.0.0 (X86 SE mode)

---

## 1) Project Overview

This repository contains the deliverables and experimental artifacts for Assignment 3:

- **Part 1 (Conceptual Paper):** Memory technologies, cache optimizations, virtual memory/VMs, and design tradeoffs.
- **Part 2 (Hands-On gem5):** Cache configuration experiments using gem5 and a custom memory benchmark.

The experiments evaluate how cache parameters influence performance metrics such as miss rate, simulated cycles (simTicks), and CPI.

## 2) Environment

- OS: Linux (Ubuntu)
- gem5: `25.1.0.0`
- Build used: `build/X86/gem5.opt`
- Mode: SE (System Call Emulation)
- Config script: `configs/deprecated/example/se.py`

Note: gem5 prints a warning that `se.py` is deprecated. It was used for compatibility with gem5 25.x and to match the course workflow.

---

## 3) Benchmark Program

A simple memory benchmark (`mem_bench.c`) is used to generate consistent memory traffic.

### Compile (example)
```bash
gcc -O2 -o mem_bench mem_bench.c
