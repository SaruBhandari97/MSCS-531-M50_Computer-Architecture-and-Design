#include <stdio.h>
#include <stdint.h>

volatile int A[1024], B[1024], C[1024];

int main() {
    for (int i = 0; i < 1024; i++) { A[i] = i; B[i] = 2*i; }
    for (int i = 0; i < 1024; i++) { C[i] = A[i] + B[i]; }

    int sum = 0;
    for (int i = 0; i < 1024; i++) {
        if ((C[i] & 1) == 0) sum += C[i];
        else sum -= C[i];
    }

    printf("sum=%d\n", sum);
    return 0;
}
