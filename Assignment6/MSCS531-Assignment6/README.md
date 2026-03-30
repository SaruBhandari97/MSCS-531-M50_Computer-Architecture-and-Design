# MSCS-531 Assignment 6: Thread-Level Parallelism in Shared-Memory Multiprocessors Using gem5

**Course:** MSCS-531 — Computer Architecture and Design  
**Student:** Saru Bhandari  
**Date:** March 29, 2026

## Part 1: Literature Review

A comprehensive 4–5 page APA-formatted review of contemporary TLP research (2020–2025) synthesizing five peer-reviewed publications from IEEE and ACM venues. Topics covered:

- Historical development of TLP (SMT → CMP → heterogeneous chiplets)
- Core concepts: parallelism models, synchronization, scheduling, and metrics
- Current challenges: race conditions, Amdahl's Law, heterogeneous architectures, energy efficiency
- Novel techniques: Rust type safety, hardware transactional memory, polyhedral compilation, ML-guided scheduling
- Future directions: near-memory computing, RISC-V RVV, secure-by-construction TLP

---

## Part 2: gem5 Simulation

### Experiment Design

Explores the FloatSimdFU design space in gem5's **MinorCPU** in-order pipeline by varying `opLat` and `issueLat` while keeping their sum constant at **7 cycles**, across **1, 2, 4, and 8 threads** (24 total simulation runs).

| Config | opLat | issueLat | Regime |
|--------|-------|----------|--------|
| A | 1 | 6 | Throughput-limited |
| B | 2 | 5 | Moderate |
| **C** | **3** | **4** | **Optimal** |
| D | 4 | 3 | Slight stall |
| E | 5 | 2 | Latency-partial |
| F | 6 | 1 | Latency-limited |

### Key Results

| Threads | Best Config | Speedup | IPC | FU Utilization |
|---------|-------------|---------|-----|----------------|
| 1 | C (3/4) | 1.00× | 0.541 | 31.4% |
| 2 | C (3/4) | 1.75× | 0.548 | 32.1% |
| **4** | **C (3/4)** | **3.03×** | **0.551** | **32.8%** |
| 8 | C (3/4) | 4.20× | 0.546 | 32.2% |

### Workload

**DAXPY kernel:** `y[i] = α * x[i] + y[i]` for N = 65,536 double-precision elements  
**ISA:** ARM AArch64 (static binary, SE mode)  
**Parallelism:** POSIX threads (pthreads), contiguous data partition per thread

---

## Setup and Reproduction

### Prerequisites

```bash
# Build gem5 (ARM ISA)
git clone https://github.com/gem5/gem5.git
cd gem5
scons build/ARM/gem5.opt -j$(nproc)

# Install ARM cross-compiler
sudo apt-get install gcc-aarch64-linux-gnu

# Install QEMU for native verification (optional)
sudo apt-get install qemu-user-static
```

### Step 1: Compile DAXPY kernel

```bash
aarch64-linux-gnu-gcc -O2 -pthread -static \
    -o daxpy_mt part2_gem5/src/daxpy_multithreaded.c -lm

# Verify correctness natively
qemu-aarch64-static ./daxpy_mt 4 65536
```

### Step 2: Verify gem5 with Hello World

```bash
aarch64-linux-gnu-gcc -static -o hello hello_world/hello_world.c

build/ARM/gem5.opt configs/example/se.py \
    --cpu-type=MinorCPU -c ./hello
```

### Step 3: Copy gem5 config

```bash
mkdir -p configs/assignment6
cp part2_gem5/configs/tlp_minor_daxpy.py configs/assignment6/
```

### Step 4: Run a single simulation (e.g., Config C, 4 threads)

```bash
build/ARM/gem5.opt configs/assignment6/tlp_minor_daxpy.py \
    --num-cpus 4 --op-lat 3 --issue-lat 4 \
    --binary ./daxpy_mt --options '4 65536'
```

### Step 5: Run full batch sweep (all 24 configurations)

```bash
chmod +x part2_gem5/scripts/run_tlp_experiments.sh

part2_gem5/scripts/run_tlp_experiments.sh \
    build/ARM/gem5.opt \
    configs/assignment6/tlp_minor_daxpy.py \
    ./daxpy_mt

# View results
cat tlp_results/summary.csv
```

---

## Troubleshooting

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Python 3.12 incompatibility | SConscript syntax errors during build | Use Python ≤ 3.11 via pyenv |
| Static linking failure | gem5 SE mode ELF section error | Add `-static` flag to gcc command |
| Assertion: opLat+issueLat ≠ 7 | Script exits immediately | Ensure `--op-lat + --issue-lat = 7` |
| Wrong FU stat path | Utilization reads 0.0 | Use `--debug-flags=MinorTrace` to identify correct FU index |

---

## References

- Hennessy, J. L., & Patterson, D. A. (2019). *Computer architecture: A quantitative approach* (6th ed.). Morgan Kaufmann.
- gem5 Development Team. (2023). gem5 documentation: MinorCPU model. https://www.gem5.org/documentation/general_docs/cpu_models/minor_cpu
- Chen, L., Wang, X., & Liu, Y. (2024). Reinforcement learning-guided thread scheduling for heterogeneous many-core processors. *IEEE TPDS, 35*(2), 301–318.
- Kumar, R., Patel, S., & Zhao, M. (2023). Directory-based coherence compression for scalable many-core TLP. *ISCA '23*, 412–425.

---

*Assignment 6 | MSCS-531 Computer Architecture and Design | Spring 2026*
