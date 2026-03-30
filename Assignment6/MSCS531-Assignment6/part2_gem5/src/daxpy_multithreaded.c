/*
 * daxpy_multithreaded.c
 * Multi-threaded DAXPY kernel for gem5 simulation (Assignment 6, Part 2)
 * Course: MSCS-531 Computer Architecture and Design
 *
 * DAXPY: y[i] = alpha * x[i] + y[i]
 *
 * Each thread handles a contiguous sub-range of the vectors.
 * Compile: gcc -O2 -pthread -o daxpy_mt daxpy_multithreaded.c -lm
 * gem5 SE mode: build/ARM/gem5.opt configs/example/se.py \
 *   --cpu-type=MinorCPU --num-cpus=4 \
 *   -c daxpy_mt -o "4 1024"
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <math.h>
#include <time.h>

/* ---- gem5 annotation macros (no-op outside simulator) ---- */
#ifndef GEM5_ANNOTATIONS
#define GEM5_ANNOTATIONS 0
#endif

#if GEM5_ANNOTATIONS
#include "m5ops.h"
#define BEGIN_ROI()  m5_work_begin(0, 0)
#define END_ROI()    m5_work_end(0, 0)
#else
#define BEGIN_ROI()  do {} while(0)
#define END_ROI()    do {} while(0)
#endif

/* ---- Constants ---- */
#define MAX_THREADS 16
#define MAX_N       (1 << 20)   /* 1M elements */

/* ---- Shared data ---- */
typedef struct {
    double  alpha;
    double *x;
    double *y;
    int     n;          /* total vector length */
    int     tid;        /* thread id */
    int     num_threads;
    double  elapsed_ns; /* filled in by each thread */
} ThreadArgs;

/* ---- Per-thread DAXPY ---- */
void *daxpy_thread(void *arg) {
    ThreadArgs *a = (ThreadArgs *)arg;

    int chunk = a->n / a->num_threads;
    int start = a->tid * chunk;
    int end   = (a->tid == a->num_threads - 1) ? a->n : start + chunk;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    BEGIN_ROI();

    for (int i = start; i < end; i++) {
        a->y[i] = a->alpha * a->x[i] + a->y[i];
    }

    END_ROI();

    clock_gettime(CLOCK_MONOTONIC, &t1);
    a->elapsed_ns = (double)(t1.tv_sec - t0.tv_sec) * 1e9 +
                    (double)(t1.tv_nsec - t0.tv_nsec);
    return NULL;
}

/* ---- Serial DAXPY (baseline) ---- */
double daxpy_serial(double alpha, double *x, double *y, int n) {
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < n; i++) {
        y[i] = alpha * x[i] + y[i];
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    return (double)(t1.tv_sec - t0.tv_sec) * 1e9 +
           (double)(t1.tv_nsec - t0.tv_nsec);
}

/* ---- Verification ---- */
int verify(double *y_ref, double *y_par, int n) {
    for (int i = 0; i < n; i++) {
        if (fabs(y_ref[i] - y_par[i]) > 1e-9) return 0;
    }
    return 1;
}

int main(int argc, char **argv) {

    int num_threads = 4;
    int n           = 65536;

    if (argc >= 2) num_threads = atoi(argv[1]);
    if (argc >= 3) n           = atoi(argv[2]);

    if (num_threads < 1 || num_threads > MAX_THREADS) {
        fprintf(stderr, "num_threads must be 1-%d\n", MAX_THREADS);
        return 1;
    }
    if (n < 1 || n > MAX_N) {
        fprintf(stderr, "n must be 1-%d\n", MAX_N);
        return 1;
    }

    double  alpha = 2.5;
    double *x     = (double *)malloc(n * sizeof(double));
    double *y     = (double *)malloc(n * sizeof(double));
    double *y_ref = (double *)malloc(n * sizeof(double));

    /* Initialize vectors */
    srand(42);
    for (int i = 0; i < n; i++) {
        x[i]     = (double)rand() / RAND_MAX;
        y[i]     = (double)rand() / RAND_MAX;
        y_ref[i] = y[i];
    }

    /* ---- Serial baseline ---- */
    double serial_ns = daxpy_serial(alpha, x, y_ref, n);

    /* ---- Parallel execution ---- */
    pthread_t   threads[MAX_THREADS];
    ThreadArgs  args[MAX_THREADS];

    /* Restore y for parallel run */
    for (int i = 0; i < n; i++) y[i] = y_ref[i] - alpha * x[i]; /* undo serial */

    struct timespec wall0, wall1;
    clock_gettime(CLOCK_MONOTONIC, &wall0);

    for (int t = 0; t < num_threads; t++) {
        args[t].alpha       = alpha;
        args[t].x           = x;
        args[t].y           = y;
        args[t].n           = n;
        args[t].tid         = t;
        args[t].num_threads = num_threads;
        args[t].elapsed_ns  = 0.0;
        pthread_create(&threads[t], NULL, daxpy_thread, &args[t]);
    }

    for (int t = 0; t < num_threads; t++) {
        pthread_join(threads[t], NULL);
    }

    clock_gettime(CLOCK_MONOTONIC, &wall1);
    double wall_ns = (double)(wall1.tv_sec - wall0.tv_sec) * 1e9 +
                     (double)(wall1.tv_nsec - wall0.tv_nsec);

    /* ---- Results ---- */
    int ok = verify(y_ref, y, n);

    printf("\n=== DAXPY Multi-Thread Benchmark ===\n");
    printf("Vector length  : %d\n", n);
    printf("Num threads    : %d\n", num_threads);
    printf("Alpha          : %.4f\n", alpha);
    printf("Correctness    : %s\n", ok ? "PASS" : "FAIL");
    printf("\n");
    printf("Serial time    : %.3f ms\n", serial_ns / 1e6);
    printf("Parallel wall  : %.3f ms\n", wall_ns  / 1e6);
    printf("Speedup        : %.2fx\n",   serial_ns / wall_ns);
    printf("Efficiency     : %.2f%%\n",  100.0 * (serial_ns / wall_ns) / num_threads);
    printf("\nPer-thread times (ms):\n");
    for (int t = 0; t < num_threads; t++) {
        printf("  Thread %2d: %.3f ms\n", t, args[t].elapsed_ns / 1e6);
    }

    free(x); free(y); free(y_ref);
    return 0;
}
