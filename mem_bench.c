#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char** argv) {
    size_t n = (argc > 1) ? (size_t)atoll(argv[1]) : (size_t)10*1000*1000; // number of elements
    int stride = (argc > 2) ? atoi(argv[2]) : 16; // access stride
    volatile uint64_t sum = 0;

    uint64_t *a = (uint64_t*)malloc(n * sizeof(uint64_t));
    if (!a) {
        perror("malloc failed");
        return 1;
    }

    // Initialize array
    for (size_t i = 0; i < n; i++) {
        a[i] = i;
    }

    // Memory access loop (creates cache pressure)
    for (int rep = 0; rep < 20; rep++) {
        for (size_t i = 0; i < n; i += stride) {
            sum += a[i];
        }
    }

    printf("Sum = %llu\n", (unsigned long long)sum);
    free(a);
    return 0;
}
