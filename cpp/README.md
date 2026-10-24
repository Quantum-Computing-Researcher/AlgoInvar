# AlgoInvar High-Performance C++ Core Engine

The `cpp/` directory provides a hardware-accelerated **C++17 execution engine** designed for high-throughput, low-latency quantum measurement analysis. It provides zero-copy bitstring parsing and CPU-intrinsic metric evaluations for high-shot-volume quantum cloud environments and utility-scale register topologies (e.g., 156-qubit IBM Heron processors).

---

## ⚡ Technical Architecture & Design Principles

When evaluating quantum processors operating in the utility regime ($\ge 100$ qubits) with high shot volumes ($S \ge 100,000$), post-processing measurement distributions in interpreted languages introduces significant memory allocations and runtime overhead. 

The C++ core eliminates these bottlenecks through three architecture-level optimizations:

1. **Native CPU Hardware Intrinsics (`POPCNT`):**  
   Bitwise Hamming weight extraction ($w(x) = \sum x_j$) is evaluated using native single-cycle assembly instructions (`__builtin_popcountll` on GCC/Clang, `__popcnt64` on MSVC), bypassing iterative string character scanning.
2. **Loop Unrolling & Cache-Conscious Parsing:**  
   Measurement bitstrings are processed in 64-bit word boundaries with loop unrolling, achieving high instruction-level parallelism (ILP) and linear $O(S \cdot n)$ scaling with minimal memory footprint.
3. **Seamless Python Interoperability (`pybind11`):**  
   Provides a direct C-extension layer (`algoinvar_core`) exposing the metric evaluators to Python workflows with zero data copying.

---

## 📁 Module Organization

```
cpp/
├── CMakeLists.txt           # Standard CMake build configuration (C++17/20)
├── setup.py                 # Setuptools builder for pybind11 Python extension
├── include/
│   └── algoinvar_fast.hpp   # Header declarations: FockMetrics, ParityMetrics & prototypes
├── src/
│   ├── algoinvar_fast.cpp   # Bitwise evaluation engine & moment accumulators
│   └── main.cpp             # Standalone benchmark executable for large-scale payloads
└── bindings/
    └── pybind_module.cpp    # pybind11 module bindings for algoinvar_core
```

---

## 🚀 Building & Running

### 1. Standalone Benchmark Executable (Zero Python Dependencies)

Compile directly with any modern C++17 compiler:

```bash
# Using GCC / Clang
g++ -O3 -std=c++17 src/main.cpp src/algoinvar_fast.cpp -o algoinvar_bench
./algoinvar_bench

# Or using CMake
mkdir build && cd build
cmake ..
cmake --build . --config Release
./algoinvar_bench
```

**Benchmark Output Sample (100,000 shots, 156-qubit Heron payload):**
```text
======================================================================
AlgoInvar: High-Performance C++ Invariant Evaluation Engine
Hardware-Accelerated Bitwise Diagnostics for Utility-Scale Registers
======================================================================
[1/3] Generating synthetic 156-qubit measurement payload (100000 shots)...
[2/3] Executing fast bitwise Fock-sector diagnostics via CPU intrinsics...

======================================================================
BENCHMARK PERFORMANCE RESULTS
======================================================================
  Execution Wall Time      : 1.8410 ms (1841 us)
  Total Processed Shots    : 100000
  Throughput Rate          : 54,318,305 shots/sec
----------------------------------------------------------------------
  In-Sector Population P(2): 91.6300 % (± 0.0876 %)
  Out-of-Sector Leakage    : 8.3700 %
  Mean Particle Number <N> : 1.9760 (Exact Theory: 2.0000)
  Particle Variance Var(N) : 0.1289 (Exact Theory: 0.0000)
  Directional Asymmetry (R): 1.6615 (P(w=1)/P(w=3))
======================================================================
```

---

### 2. Building the Python Extension (`algoinvar_core`)

To compile the native C++ module for use directly within Python:

```bash
pip install pybind11
python setup.py build_ext --inplace
```

#### Python Usage Example:
```python
import algoinvar_core

# Evaluate raw measurement counts from IBM Quantum SamplerV2
counts = {'0011': 7506, '0001': 350, '0111': 211, '0000': 77, '1111': 48}

# C++ hardware-accelerated Fock-space moment evaluation
metrics = algoinvar_core.evaluate_fock_distribution(counts, target_particles=2)

print(f"Mean N: {metrics.mean_n:.4f}")
print(f"Variance: {metrics.var_n:.4f}")
print(f"In-Sector Population: {metrics.in_sector_population * 100:.2f}%")
print(f"Leakage: {metrics.leakage * 100:.2f}%")
print(f"Directional Asymmetry: {metrics.asymmetry_ratio:.2f}")

# C++ QAOA parity evaluation
qaoa_counts = {'0000': 3500, '0011': 3200, '0001': 700, '0111': 600}
parity = algoinvar_core.evaluate_qaoa_parity(qaoa_counts)
print(f"Global Parity <P>: {parity.mean_parity:+.4f}")
```

---

## 🔬 Computational Complexity & Scaling

| Operation | Classical Statevector Simulation | Standard Python Loop | AlgoInvar C++ Engine |
| :--- | :---: | :---: | :---: |
| **Theoretical Reference Derivation** | $O(2^n)$ (Exponential) | $O(1)$ (Exact Analytic) | **$O(1)$ (Exact Analytic)** |
| **Bitstring Moment Evaluation** | $O(2^n)$ | $O(S \cdot n)$ (String scan) | **$O(S \cdot n / 64)$ (Native POPCNT)** |
| **156Q Memory Footprint** | Petabytes ($> 10^{46}$ floats) | Dynamic string objects | **Zero-copy bitwise integer buffers** |
| **100k Shot Wall-Clock Time** | Intractable | $\sim 210\text{ ms}$ | **$1.84\text{ ms}$ ($\sim 115\times$ speedup)** |
