#include <stdio.h>
#include <stdint.h>

volatile int A[200000];

int main() {
    for (int i=0;i<200000;i++) A[i]=i;

    int sum=0;
    for (int i=0;i<200000;i++) {
        if ((A[i] ^ (i*3)) & 1) sum += A[i];
        else sum -= A[i];
    }
    printf("sum=%d\n", sum);
    return 0;
}
