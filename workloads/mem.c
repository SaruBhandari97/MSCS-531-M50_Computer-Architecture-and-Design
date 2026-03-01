#include <stdio.h>
volatile int X[5000000];

int main() {
    long long s=0;
    for (int i=0;i<5000000;i++) X[i]=i;
    for (int i=0;i<5000000;i++) s += X[i];
    printf("s=%lld\n", s);
    return 0;
}
