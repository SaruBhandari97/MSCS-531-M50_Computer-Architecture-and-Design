/*
 * hello_world.c
 * gem5 SE mode verification program — Assignment 6, MSCS-531
 * saruBhandari@ubuntu
 *
 * Compile: aarch64-linux-gnu-gcc -static -o hello hello_world.c
 * Run in gem5:
 *   build/ARM/gem5.opt configs/example/se.py \
 *     --cpu-type=MinorCPU -c ./hello
 */

#include <stdio.h>

int main(void) {
    printf("Hello World from gem5!\n");
    printf("MinorCPU ARM SE mode — verification successful.\n");
    return 0;
}
