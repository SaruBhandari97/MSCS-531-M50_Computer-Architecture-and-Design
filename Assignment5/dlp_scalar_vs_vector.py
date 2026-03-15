import numpy as np
import time
import matplotlib.pyplot as plt

# Input sizes
sizes = [10000, 50000, 100000, 500000, 1000000]

scalar_times = []
vector_times = []

# Scalar implementation
def scalar_add(a, b):
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

print("\nRunning Scalar vs Vector (SIMD-style) DLP Experiment\n")
print("--------------------------------------------------------------")
print("{:<12} {:<18} {:<18}".format("Input Size", "Scalar Time (s)", "Vector Time (s)"))
print("--------------------------------------------------------------")

for size in sizes:

    A = np.random.rand(size)
    B = np.random.rand(size)

    # Scalar computation
    start = time.time()
    scalar_add(A, B)
    end = time.time()

    scalar_time = end - start
    scalar_times.append(scalar_time)

    # Vector computation (SIMD-style)
    start = time.time()
    C = A + B
    end = time.time()

    vector_time = end - start
    vector_times.append(vector_time)

    print("{:<12} {:<18.6f} {:<18.6f}".format(size, scalar_time, vector_time))

print("--------------------------------------------------------------")

# Plot results
plt.figure(figsize=(8,5))
plt.plot(sizes, scalar_times, marker='o', label="Scalar Implementation")
plt.plot(sizes, vector_times, marker='o', label="Vectorized (SIMD-style) Implementation")

plt.xlabel("Input Size")
plt.ylabel("Execution Time (seconds)")
plt.title("Scalar vs Vector (SIMD-style) Performance")
plt.legend()
plt.grid(True)

plt.savefig("scalar_vs_vector_performance.png")

print("\nGraph saved as: scalar_vs_vector_performance.png")

plt.show()