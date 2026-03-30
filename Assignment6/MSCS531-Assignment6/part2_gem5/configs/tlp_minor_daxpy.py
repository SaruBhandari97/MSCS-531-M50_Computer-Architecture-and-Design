#!/usr/bin/env python3
"""
tlp_minor_daxpy.py — gem5 configuration script
Assignment 6, Part 2: FloatSimdFU Design Space Exploration
Course: MSCS-531 Computer Architecture and Design

Usage (from gem5 root):
    build/ARM/gem5.opt configs/assignment6/tlp_minor_daxpy.py \
        --num-cpus 4 --op-lat 3 --issue-lat 4 \
        --binary ./daxpy_mt --options "4 65536"

Explores opLat + issueLat = 7 combinations across thread counts.
"""

import argparse
import os
import sys

import m5
from m5.objects import *
from m5.util import addToPath

# --------------------------------------------------------------------------
# Argument parsing
# --------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="gem5 MinorCPU DAXPY TLP experiment")
parser.add_argument("--num-cpus",   type=int, default=4,
                    help="Number of CPU cores (= thread count for SE mode)")
parser.add_argument("--op-lat",     type=int, default=3,
                    help="FloatSimdFU opLat (cycles)")
parser.add_argument("--issue-lat",  type=int, default=4,
                    help="FloatSimdFU issueLat (cycles); opLat+issueLat should =7")
parser.add_argument("--binary",     type=str, default="./daxpy_mt",
                    help="Path to compiled daxpy binary")
parser.add_argument("--options",    type=str, default="4 65536",
                    help="Arguments passed to the binary")
args = parser.parse_args()

assert args.op_lat + args.issue_lat == 7, \
    f"opLat ({args.op_lat}) + issueLat ({args.issue_lat}) must equal 7"

# --------------------------------------------------------------------------
# Custom FloatSimd FU with configurable latencies
# --------------------------------------------------------------------------
class CustomFloatSimdFU(MinorFU):
    opClasses = minorMakeOpClassSet([
        'FloatAdd', 'FloatCmp', 'FloatCvt', 'FloatMult', 'FloatMultAcc',
        'FloatDiv', 'FloatSqrt', 'SimdAdd', 'SimdAddAcc', 'SimdAlu',
        'SimdCmp', 'SimdCvt', 'SimdMisc', 'SimdMult', 'SimdMultAcc',
        'SimdShift', 'SimdShiftAcc', 'SimdFloatAdd', 'SimdFloatAlu',
        'SimdFloatCmp', 'SimdFloatCvt', 'SimdFloatDiv', 'SimdFloatMisc',
        'SimdFloatMult', 'SimdFloatMultAcc', 'SimdFloatSqrt',
        'SimdReduceAdd', 'SimdReduceAlu', 'SimdReduceCmp',
        'SimdFloatReduceAdd', 'SimdFloatReduceCmp',
        'SimdAes', 'SimdAesMix', 'SimdSha1Hash', 'SimdSha1Hash2',
        'SimdSha256Hash', 'SimdSha256Hash2', 'SimdShaSigma2',
        'SimdShaSigma4', 'SimdPredAlu', 'Matrix', 'MatrixMov',
        'MatrixOP',
    ])
    opLat    = args.op_lat
    issueLat = args.issue_lat


class CustomFUPool(MinorFUPool):
    funcUnits = [
        # Integer ALU (unchanged)
        MinorFU(opClasses=minorMakeOpClassSet(['IntAlu']),      opLat=3, issueLat=1),
        MinorFU(opClasses=minorMakeOpClassSet(['IntAlu']),      opLat=3, issueLat=1),
        # Integer multiply/divide
        MinorFU(opClasses=minorMakeOpClassSet(['IntMult']),     opLat=3, issueLat=1),
        MinorFU(opClasses=minorMakeOpClassSet(['IntDiv']),      opLat=9, issueLat=9),
        # Load/Store
        MinorFU(opClasses=minorMakeOpClassSet(['MemRead','FloatMemRead']),  opLat=1, issueLat=1),
        MinorFU(opClasses=minorMakeOpClassSet(['MemWrite','FloatMemWrite']),opLat=1, issueLat=1),
        # Miscellaneous
        MinorFU(opClasses=minorMakeOpClassSet(['IprAccess']),   opLat=3, issueLat=1),
        # Configurable FloatSimd unit (the subject of exploration)
        CustomFloatSimdFU(),
    ]


# --------------------------------------------------------------------------
# System configuration
# --------------------------------------------------------------------------
system = System()
system.clk_domain     = SrcClockDomain(clock='1GHz',
                                        voltage_domain=VoltageDomain())
system.mem_mode       = 'timing'
system.mem_ranges     = [AddrRange('512MB')]

# Shared memory bus
system.membus = SystemXBar()

# Create one MinorCPU per requested core
system.cpu = [MinorCPU(cpu_id=i) for i in range(args.num_cpus)]

for cpu in system.cpu:
    cpu.clk_domain = system.clk_domain
    cpu.executeFuncUnits = CustomFUPool()
    # L1 caches
    cpu.icache = Cache(size='16kB', assoc=2,
                       tag_latency=2, data_latency=2,
                       response_latency=2, mshrs=4, tgts_per_mshr=20)
    cpu.dcache = Cache(size='16kB', assoc=2,
                       tag_latency=2, data_latency=2,
                       response_latency=2, mshrs=4, tgts_per_mshr=20)
    cpu.icache.cpu_side = cpu.icache_port
    cpu.dcache.cpu_side = cpu.dcache_port
    cpu.icache.mem_side = system.membus.cpu_side_ports
    cpu.dcache.mem_side = system.membus.cpu_side_ports
    cpu.createInterruptController()
    cpu.interrupts[0].pio  = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# System port
system.system_port = system.membus.cpu_side_ports

# DRAM
system.mem_ctrl             = MemCtrl()
system.mem_ctrl.dram        = DDR3_1600_8x8()
system.mem_ctrl.dram.range  = system.mem_ranges[0]
system.mem_ctrl.port        = system.membus.mem_side_ports

# --------------------------------------------------------------------------
# Workload: multi-threaded daxpy binary
# --------------------------------------------------------------------------
binary  = args.binary
options = args.options.split()

process = Process()
process.executable = binary
process.cmd        = [binary] + options

for cpu in system.cpu:
    cpu.workload = process
    cpu.createThreads()

# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"\n[gem5] Starting simulation:")
print(f"  CPUs       = {args.num_cpus}")
print(f"  opLat      = {args.op_lat}")
print(f"  issueLat   = {args.issue_lat}")
print(f"  Binary     = {binary} {args.options}\n")

exit_event = m5.simulate()

print(f"\n[gem5] Simulation complete at tick {m5.curTick()}")
print(f"[gem5] Exit cause: {exit_event.getCause()}")
