import numpy as np
import time

sizes = [10000, 50000, 100000, 500000, 1000000]

print("\nRunning Loop-Level Parallelism Test\n")
print("--------------------------------------------------------------")
print("{:<12} {:<18} {:<18}".format("Input Size", "Loop Time (s)", "Vector Time (s)"))
print("--------------------------------------------------------------")

for size in sizes:

    A = np.random.rand(size)
    B = np.random.rand(size)

    # Loop implementation
    start = time.time()
    C = [A[i] + B[i] for i in range(size)]
    end = time.time()

    loop_time = end - start

    # Vectorized implementation
    start = time.time()
    C = A + B
    end = time.time()

    vector_time = end - start

    print("{:<12} {:<18.6f} {:<18.6f}".format(size, loop_time, vector_time))

print("--------------------------------------------------------------")
print("\nLoop-level parallelism demonstrates how vectorized operations reduce execution time.")