#!/usr/bin/env bash
# run_tlp_experiments.sh
# Sweeps all (opLat, issueLat) pairs summing to 7 across thread counts 1,2,4,8
# Prerequisites: gem5 built, daxpy_mt compiled, config script in place
#
# Usage: ./run_tlp_experiments.sh [gem5_binary] [config_script] [daxpy_binary]

GEM5=${1:-"./build/ARM/gem5.opt"}
CONFIG=${2:-"./configs/assignment6/tlp_minor_daxpy.py"}
DAXPY=${3:-"./daxpy_mt"}
OUTDIR="tlp_results"
N=65536   # vector size

mkdir -p "$OUTDIR"

echo "op_lat,issue_lat,num_threads,sim_ticks,speedup" > "$OUTDIR/summary.csv"

for OPLAT in 1 2 3 4 5 6; do
    ISSLAT=$((7 - OPLAT))
    for THREADS in 1 2 4 8; do
        TAG="op${OPLAT}_iss${ISSLAT}_t${THREADS}"
        OUTFILE="$OUTDIR/${TAG}.txt"

        echo "Running: opLat=$OPLAT issueLat=$ISSLAT threads=$THREADS ..."

        $GEM5 --outdir="$OUTDIR/${TAG}" \
              $CONFIG \
              --num-cpus $THREADS \
              --op-lat   $OPLAT \
              --issue-lat $ISSLAT \
              --binary   $DAXPY \
              --options  "$THREADS $N" \
              > "$OUTFILE" 2>&1

        # Extract sim_ticks from stats.txt
        TICKS=$(grep "^sim_ticks" "$OUTDIR/${TAG}/stats.txt" 2>/dev/null \
                | awk '{print $2}' | head -1)
        TICKS=${TICKS:-"N/A"}

        echo "$OPLAT,$ISSLAT,$THREADS,$TICKS" >> "$OUTDIR/summary.csv"
        echo "  -> ticks: $TICKS"
    done
done

echo ""
echo "All experiments complete. Results in $OUTDIR/summary.csv"
