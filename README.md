# AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA

[<img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23627340.svg" height="20" alt="DOI: 10.5281/zenodo.23627340">](https://doi.org/10.5281/zenodo.23627340) [<img src="https://img.shields.io/badge/Guide-How%20To%20Run-teal.svg" height="20" alt="Guide: How To Run">](HOW_TO_RUN.md) [<img src="https://img.shields.io/badge/Scaling%20Suite-n%3D4..64-purple.svg" height="20" alt="Scaling Suite: n=4..64">](03_algoinvar_multiwidth_register_scaling/HOW_TO_RUN_SCALING.md) [<img src="https://img.shields.io/badge/License-CC%20BY--NC%204.0-blue.svg" height="20" alt="License: CC BY-NC 4.0">](LICENSE.md) [<img src="https://img.shields.io/badge/Python-3.9+-green.svg" height="20" alt="Python 3.9+">](https://www.python.org/downloads/) [<img src="https://img.shields.io/badge/Qiskit-1.0+-613394.svg" height="20" alt="Qiskit 1.0+">](https://qiskit.org/)

> 📖 **Quick Start:** For step-by-step installation, Python API usage, IBM hardware execution, multi-width register scaling ($n = 4 \to 64$), and Experiment 2 reproduction guides, see [**HOW_TO_RUN.md**](HOW_TO_RUN.md) and [**03_algoinvar_multiwidth_register_scaling/HOW_TO_RUN_SCALING.md**](03_algoinvar_multiwidth_register_scaling/HOW_TO_RUN_SCALING.md).

**AlgoInvar** is an in situ, simulation-free, parameter-free quantum hardware benchmarking and characterization framework anchored to exact algebraic conservation laws and continuous physical symmetries in algorithmically relevant workloads: **Variational Quantum Eigensolver (VQE)** fermionic chemistry and the **Quantum Approximate Optimization Algorithm (QAOA)** combinatorial optimization.

Validated on two independent 156-qubit IBM Heron r2 utility-era processors (`ibm_kingston` and `ibm_fez`) across **573,440 physical measurement shots** (`70` compiled ISA circuits in **`163.0 seconds` of cumulative QPU runtime**), AlgoInvar spans both a baseline $n = 4$ characterization (`40,960` shots in `13.0 s` QPU time per processor) and a multi-width register scaling campaign across **$n \in \{4, 8, 12, 16, 32, 64\}$ qubits** (`245,760` shots across `30` batched ISA circuits in `68.0–69.0 s` QPU time per processor)—crossing the **50-qubit classical statevector simulation threshold** with $O(1)$ analytical reference complexity, linear $O(S \cdot n)$ bitstring post-processing, and zero tensor-network or statevector simulation.

---

## 💡 Operational Capabilities & Utility-Scale Value

As quantum processors scale beyond 50–100 physical qubits, hardware evaluation faces steep computational and operational bottlenecks:

### 1. High QPU Execution Efficiency via Single-Job ISA Batching
* **Challenge:** Standard characterization methods such as Quantum State Tomography (QST), multi-seed Randomized Benchmarking (RB), or Cross-Entropy Benchmarking (XEB) require hundreds of separate circuit submissions.
* **AlgoInvar Capability:** Through single-job Instruction Set Architecture (ISA) batching via Qiskit Runtime `SamplerV2`, AlgoInvar evaluates 5 algorithmically structured circuits ($40,960$ physical shots) in **`13.0 s` of QPU time** for a single register width, or **30 circuits across six register widths $n \in \{4, 8, 12, 16, 32, 64\}$ ($245,760$ physical shots) in `68.0–69.0 s` of QPU time**.

### 2. Zero Classical Statevector Simulation ($O(1)$ Reference Derivation)
* **Challenge:** Holistic fidelity benchmarks such as XEB and Quantum Volume (QV) rely on comparing measured sample frequencies against classically simulated ideal output distributions ($O(2^n)$ complexity), which requires $16\text{ PiB}$ of memory at $n = 50$ and $295\text{ EiB}$ at $n = 64$.
* **AlgoInvar Capability:** Reference invariant values in AlgoInvar ($\langle \hat{N} \rangle \equiv N_e$, $\text{Var}(\hat{N}) \equiv 0$, $\langle \hat{\mathcal{P}} \rangle \equiv +1$, $F_{\text{echo}} \equiv 1$) are exact algebraic conservation theorems known analytically *a priori*. Deriving the theoretical reference requires **$O(1)$ classical compute**, followed by linear $O(S \cdot n)$ bitstring post-processing (accelerated to $O(S \cdot \lceil n/64 \rceil)$ via 64-bit hardware `POPCNT` CPU intrinsics in [`04_algoinvar_cpp_acceleration_engine/`](04_algoinvar_cpp_acceleration_engine/README.md)).

### 3. Two-Stage Calibration Auditing, Spatial Defect Localization & In Situ SPAM Deconvolution
* **Challenge:** In shared cloud execution environments, long queue residency times ($\Delta t_{\text{queue}} > \tau_{\text{cal}}$) can invalidate compile-time qubit layouts before execution begins, while detector dark counts ($\varepsilon_{0\to 1}$) obscure active gate fidelity on wide registers.
* **AlgoInvar Capability:**
  * **Two-Stage Calibration Audit ($t_{\text{submit}}$ vs. $t_{\text{exec}}$):** Detects temporal queue-induced calibration drift and triggers late-bound just-in-time (JIT) re-transpilation.
  * **Zero-Cost In Situ Spectator-Readout Deconvolution:** Simultaneously extracts the live per-qubit spectator dark-count rate $\hat{\varepsilon}_{0\to 1} = \langle \hat{N}_{\text{spec}} \rangle / (n - 4)$ and deconvolved active-light-cone invariants ($\langle \hat{N}_{\text{act}} \rangle$, $P_{\text{act}}(w=2)$, $F_{\text{echo}}^{\text{act}}$) directly from the algorithmic bitstrings without separate M3/TREX calibration circuits—restoring **$87.29\% \pm 0.37\%$** (`ibm_kingston`) and **$82.85\% \pm 0.42\%$** (`ibm_fez`) VQE in-sector confinement at **$n = 64$ qubits**.

---

## 📁 Repository Directory Structure & File Inventory

```text
AlgoInvar/
├── README.md                        # Comprehensive master repository documentation
├── HOW_TO_RUN.md                    # Step-by-step execution guide for all workflows
├── LICENSE.md                       # Licensing terms (CC BY-NC 4.0 & alternative licensing)
├── algoinvar research paper/        # APS PRX Quantum / RevTeX 4.2 manuscript & bibliography
├── pyproject.toml                   # Python project configuration and package metadata
├── requirements.txt                 # Python dependencies (Qiskit 1.0+, NumPy, Pandas, Matplotlib)
│
├── 03_algoinvar_multiwidth_register_scaling/               # Campaign 2: Multi-Width Register Scaling Suite (n = 4, 8, 12, 16, 32, 64)
│   ├── HOW_TO_RUN_SCALING.md        # Step-by-step guide for register-width scaling experiments
│   ├── qubit_chain_scaling.py       # Calibration-guided greedy DFS chain selector for n = 4..64
│   ├── scaling_circuits.py          # Parametric VQE & QAOA circuit builders for arbitrary width n
│   ├── scaling_metrics.py           # 4-tab Excel workbook & vector PDF/PNG figure exporter
│   ├── scaling_runner.py            # Unified execution engine (Simulation, Hardware, Reverification)
│   ├── run_scaling_kingston.py      # Scaling CLI driver for 156Q ibm_kingston (Job: dbhkepune4hc73bd3bg0)
│   ├── run_scaling_fez.py           # Scaling CLI driver for 156Q ibm_fez (Job: dbhm1hmne4hc73bd64f0)
│   ├── results_scaling_kingston/    # Verified n=4..64 datasets (245,760 shots, 69.0s QPU time)
│   └── results_scaling_fez/         # Verified n=4..64 datasets (245,760 shots, 68.0s QPU time)
│
├── 01_algoinvar_n4_hardware_baseline/                       # Campaign 1 Baseline ($n = 4$) & Core Python Library
│   ├── run_ibm_kingston.py          # Campaign 1 CLI driver (n=4 baseline) for 156Q IBM Kingston
│   ├── run_ibm_fez.py               # Campaign 1 CLI driver (n=4 baseline) for 156Q IBM Fez
│   ├── results_kingston/            # Campaign 1 Datasets: ibm_kingston (Job: dbb4hehgv2cc73e7oq40, 40,960 shots)
│   ├── results_fez/                 # Campaign 1 Datasets: ibm_fez (Job: dbb4ja9gv2cc73e7oue0, 40,960 shots)
│   ├── benchmarks/                  # Algebraic invariant evaluators (VQE & QAOA)
│   ├── circuits/                    # Excitation-conserving Givens & Max-Cut QAOA circuit builders
│   ├── hardware/                    # IBM Quantum Runtime SamplerV2 & calibration chain routing
│   └── metrics/                     # Statistical estimators, Excel export & figure generators
│
├── 04_algoinvar_cpp_acceleration_engine/                             # High-Performance C++17 Bitstring Post-Processing Engine (NO simulation)
│   ├── README.md                    # C++17 POPCNT architecture & pybind11 build guide
│   ├── CMakeLists.txt               # CMake build configuration (C++17)
│   ├── setup.py                     # Setuptools builder for pybind11 Python extension (algoinvar_core)
│   ├── include/
│   │   └── algoinvar_fast.hpp       # Header definitions: FockMetrics, ParityMetrics & POPCNT intrinsics
│   ├── src/
│   │   ├── algoinvar_fast.cpp       # O(S * ceil(n/64)) bitwise Hamming-weight & parity evaluator
│   │   └── main.cpp                 # Standalone bitstring post-processing throughput benchmark (156Q)
│   └── bindings/
│       └── pybind_module.cpp        # pybind11 module bindings for algoinvar_core
│
├── 02_algoinvar_noise_sweeps_and_mitigation/                # Controlled Kraus Noise Calibration & H2 Symmetry Mitigation Suite
│   ├── run_all_experiments.py       # Unified CLI runner for 4-channel noise sweeps & H2 mitigation
│   ├── circuits/                    # 4-qubit Givens VQE, H2 Hamiltonian, and QAOA ring circuits
│   ├── simulation/                  # Kraus noise sweeps (T1, T2*, coherent, SPAM) & H2 post-selection
│   ├── analysis/                    # Vector figure generators
│   └── results/                     # JSON records, multi-tab Excel workbooks & vector figures
│
├── device calibrations/             # Archived IBM Quantum Calibration Telemetry CSVs
│   ├── Other Experiments/           # Baseline Campaign 1 calibration snapshots (19 Oct 2026)
│   └── Scaling Experiment 29 Oct/   # Multi-width Campaign 2 calibration snapshots (29 Oct 2026)
└── tests/                           # Automated unit test suite
    └── test_invariants.py           # Verification of exact algebraic commutation & invariant identities
```

---

## 📊 Empirical Validation on 156-Qubit IBM Heron r2 Hardware (`573,440` Total Shots)

AlgoInvar was validated on two independent 156-qubit IBM Heron r2 superconducting processors (`ibm_kingston` and `ibm_fez`) across two experimental campaigns totaling **`573,440` physical measurement shots** in **`163.0 seconds` of cumulative QPU execution time**:

### Campaign 1: Baseline $n = 4$ Cross-Processor Characterization (`40,960` Shots / Device, `13.0 s` QPU Time)
* **`ibm_kingston` (Job ID: `dbb4hehgv2cc73e7oq40`):** Chain $[50, 49, 48, 47]$ ($\bar{\epsilon}_{\text{CZ}} = 0.194\%$, $T_1 = 272.3\ \mu\text{s}$).
  * VQE $\langle \hat{N} \rangle = 1.9760 \pm 0.0040$, $\text{Var}(\hat{N}) = 0.1289 \pm 0.0060$, In-Sector $P(w=2) = 91.63\% \pm 0.31\%$, $\mathcal{L}_{\text{leak}} = 8.37\% \pm 0.31\%$, $R_{\text{asym}} = 1.66 \pm 0.14$, VQE Echo $F_{\text{echo}} = 0.8083 \pm 0.0043$, QAOA Parity $\langle \hat{\mathcal{P}} \rangle_{p=1} = +0.8257 \pm 0.0062$, $\langle \hat{\mathcal{P}} \rangle_{p=2} = +0.7334 \pm 0.0075$, QAOA Echo ($p=2$) $= 0.7562 \pm 0.0047$.
* **`ibm_fez` (Job ID: `dbb4ja9gv2cc73e7oue0`):** Chain $[109, 110, 111, 98]$ ($\bar{\epsilon}_{\text{CZ}} = 0.215\%$, $T_1 = 146.8\ \mu\text{s}$).
  * VQE $\langle \hat{N} \rangle = 1.9403 \pm 0.0044$, $\text{Var}(\hat{N}) = 0.1616 \pm 0.0062$, In-Sector $P(w=2) = 88.39\% \pm 0.35\%$, $\mathcal{L}_{\text{leak}} = 11.61\% \pm 0.35\%$, $R_{\text{asym}} = 3.00 \pm 0.24$, VQE Echo $F_{\text{echo}} = 0.8013 \pm 0.0044$, QAOA Parity $\langle \hat{\mathcal{P}} \rangle_{p=1} = +0.7847 \pm 0.0068$, $\langle \hat{\mathcal{P}} \rangle_{p=2} = +0.6860 \pm 0.0080$, QAOA Echo ($p=2$) $= 0.6848 \pm 0.0051$.

### Campaign 2: Multi-Width Register Scaling $n \in \{4, 8, 12, 16, 32, 64\}$ Across the 50-Qubit Classical Simulation Threshold (`245,760` Shots / Device)
* **`ibm_kingston` (`Job ID: dbhkepune4hc73bd3bg0`, `69.0 s` QPU time, High-Queue Drift Regime)** and **`ibm_fez` (`Job ID: dbhm1hmne4hc73bd64f0`, `68.0 s` QPU time, Low-Queue Synchronous Regime)**:

| Processor | Width $n$ | Raw Full-Reg. $\langle\hat{N}\rangle$ | Raw In-Sector $P(w=2)$ | Raw Asymmetry $R_{\text{asym}}$ | Raw VQE Echo $F_{\text{echo}}$ | Spectator Dark Rate $\hat{\varepsilon}_{0\to 1}$ | Deconvolved $P_{\text{act}}(w=2)$ | Deconvolved Echo $F_{\text{echo}}^{\text{act}}$ | QAOA Parity $\langle\hat{\mathcal{P}}\rangle_{p=1}$ | Bounded-$k$ QAOA $F_{\text{echo}}^{(k=4)} / F_{\text{echo}}^{(k=1)}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`ibm_kingston`** | $4$ | $1.8773 \pm 0.0045$ | $84.56\% \pm 0.40\%$ | $7.42 \pm 0.66$ | $0.7417$ | --- | $84.56\%$ | $0.7417$ | $+0.6738$ | $58.25\% / 80.68\%$ |
| | $8$ | $2.1312 \pm 0.0070$ | $83.68\% \pm 0.41\%$ | $0.61 \pm 0.04$ | $0.7557$ | $6.62\%/\text{q}$ | $78.30\%$ | $0.8195$ | $+0.5530$ | $37.83\% / 75.65\%$ |
| | $12$ | $2.1432 \pm 0.0078$ | $79.13\% \pm 0.45\%$ | $0.66 \pm 0.04$ | $0.6472$ | $3.18\%/\text{q}$ | $80.24\%$ | $0.7528$ | $+0.2441$ | $22.38\% / 67.08\%$ |
| | $16$ | $2.3455 \pm 0.0099$ | $72.03\% \pm 0.50\%$ | $0.38 \pm 0.02$ | $0.5804$ | $3.22\%/\text{q}$ | **$88.16\%$** | **$0.8217$** | $-0.0115$ | $9.48\% / 53.83\%$ |
| | $32$ | $5.3302 \pm 0.0201$ | $3.69\% \pm 0.21\%$ | $0.03 \pm 0.01$ | $0.0057$ | **$12.04\%/\text{q}$** | **$87.08\%$** | **$0.8164$** | $+0.0286$ | $8.90\% / 55.15\%$ |
| | **$64$** | **$3.9094 \pm 0.0208$** | **$24.79\% \pm 0.48\%$** | **$0.09 \pm 0.01$** | **$0.0991$** | **$3.25\%/\text{q}$** | **$87.29\%$** | **$0.7878$** | $+0.0022$ | **$9.60\% / 55.54\%$** |
| **`ibm_fez`** | **$4$** | **$1.9799 \pm 0.0036$** | **$92.04\% \pm 0.30\%$** | **$1.78 \pm 0.15$** | **$0.8276$** | --- | **$92.04\%$** | **$0.8276$** | **$+0.8271$** | **$49.78\% / 81.32\%$** |
| | $8$ | $2.1111 \pm 0.0065$ | $83.42\% \pm 0.41\%$ | $0.67 \pm 0.04$ | $0.7089$ | $6.68\%/\text{q}$ | $77.27\%$ | $0.7948$ | $+0.3035$ | $18.10\% / 65.39\%$ |
| | $12$ | $1.9551 \pm 0.0107$ | $49.71\% \pm 0.55\%$ | $2.28 \pm 0.08$ | $0.2429$ | $4.24\%/\text{q}$ | $51.92\%$ | $0.3207$ | $+0.0098$ | $10.42\% / 57.38\%$ |
| | $16$ | $2.5439 \pm 0.0115$ | $62.06\% \pm 0.54\%$ | $0.21 \pm 0.01$ | $0.4462$ | $4.86\%/\text{q}$ | **$88.40\%$** | **$0.7902$** | $+0.0051$ | $18.63\% / 62.58\%$ |
| | $32$ | $3.3234 \pm 0.0180$ | $36.24\% \pm 0.53\%$ | $0.20 \pm 0.01$ | $0.1976$ | $4.91\%/\text{q}$ | **$82.70\%$** | **$0.7271$** | $+0.0161$ | $10.72\% / 56.78\%$ |
| | **$64$** | **$6.0916 \pm 0.0270$** | **$4.19\% \pm 0.22\%$** | **$0.04 \pm 0.01$** | **$0.0065$** | **$6.91\%/\text{q}$** | **$82.85\%$** | **$0.7095$** | $-0.0076$ | **$12.28\% / 58.84\%$** |

---

## ⚡ AlgoInvar High-Performance C++17 Bitstring Post-Processing Engine (`04_algoinvar_cpp_acceleration_engine/`)

> **Important Note on Purpose:** The [`04_algoinvar_cpp_acceleration_engine/`](04_algoinvar_cpp_acceleration_engine/) directory is **not** a classical quantum statevector simulator. In accordance with AlgoInvar's simulation-free framework, `04_algoinvar_cpp_acceleration_engine/` implements the **linear $O(S \cdot \lceil n/64 \rceil)$ classical bitstring post-processing engine** that computes Hamming weights $\text{wt}(x) = \sum x_j$, Fock-sector populations $P(w)$, and $X$-basis parity eigenvalues $(-1)^{\sum y_j}$ from hardware measurement bitstrings using native 64-bit CPU `POPCNT` intrinsics (`__popcnt64` / `__builtin_popcountll`).

By packing wide measurement bitstrings ($n = 64$ to $156$ qubits) into 64-bit integer words and invoking single-cycle hardware population-count instructions, `04_algoinvar_cpp_acceleration_engine/` evaluates $100,000$ shots of 156-qubit bitstrings in **$1.84\text{ ms}$** ($\sim 5.4 \times 10^7\text{ shots/sec}$, a $115\times$ speedup over character-by-character Python loops) with zero $O(2^n)$ statevector allocation. It includes both a standalone C++17 benchmark executable and native Python bindings via `pybind11` (`algoinvar_core`). See [`04_algoinvar_cpp_acceleration_engine/README.md`](04_algoinvar_cpp_acceleration_engine/README.md) for complete build details.

---

## 🚀 Execution Guide & CLI Commands

### 1. Campaign 1 Baseline Drivers ($n = 4$, `run_ibm_kingston.py` & `run_ibm_fez.py`)
```bash
# Mode 1: Local noiseless simulation baseline (0 QPU seconds)
python 01_algoinvar_n4_hardware_baseline/run_ibm_kingston.py
python 01_algoinvar_n4_hardware_baseline/run_ibm_fez.py

# Mode 2: Physical hardware execution on 156Q Heron r2 (40,960 shots, ~13.0s QPU time)
python 01_algoinvar_n4_hardware_baseline/run_ibm_kingston.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 01_algoinvar_n4_hardware_baseline/run_ibm_fez.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"

# Mode 3: Offline reverification of completed Job IDs (0 QPU seconds)
python 01_algoinvar_n4_hardware_baseline/run_ibm_kingston.py --job-id "dbb4hehgv2cc73e7oq40" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 01_algoinvar_n4_hardware_baseline/run_ibm_fez.py --job-id "dbb4ja9gv2cc73e7oue0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
```

### 2. Campaign 2 Multi-Width Register Scaling Drivers ($n = 4, 8, 12, 16, 32, 64$, `03_algoinvar_multiwidth_register_scaling/`)
```bash
# Mode 1: Local simulation mode (0 QPU seconds)
python 03_algoinvar_multiwidth_register_scaling/run_scaling_kingston.py
python 03_algoinvar_multiwidth_register_scaling/run_scaling_fez.py

# Mode 2: Physical hardware execution across n=4..64 (245,760 shots, ~68-69s QPU time)
python 03_algoinvar_multiwidth_register_scaling/run_scaling_kingston.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 03_algoinvar_multiwidth_register_scaling/run_scaling_fez.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"

# Mode 3: Offline reverification of completed scaling Job IDs (0 QPU seconds)
python 03_algoinvar_multiwidth_register_scaling/run_scaling_kingston.py --job-id "dbhkepune4hc73bd3bg0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 03_algoinvar_multiwidth_register_scaling/run_scaling_fez.py --job-id "dbhm1hmne4hc73bd64f0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
```

### 3. Controlled Kraus Noise & $\mathrm{H}_2$ Symmetry Mitigation Suite (`02_algoinvar_noise_sweeps_and_mitigation/`)
```bash
python 02_algoinvar_noise_sweeps_and_mitigation/run_all_experiments.py
```

### 4. C++17 Bitstring Post-Processing Engine (`04_algoinvar_cpp_acceleration_engine/`) & Unit Tests (`tests/`)
```bash
# Run automated unit tests for exact algebraic invariants
python -m unittest tests/test_invariants.py

# Compile and run the C++17 POPCNT bitstring throughput benchmark
cd 04_algoinvar_cpp_acceleration_engine
g++ -O3 -std=c++17 src/main.cpp src/algoinvar_fast.cpp -o algoinvar_bench
./algoinvar_bench
```

---

## 📜 Citation & Licensing

If you use AlgoInvar in your research, please cite:

* **Permanent DOI:** [https://doi.org/10.5281/zenodo.23627340](https://doi.org/10.5281/zenodo.23627340)

```bibtex
@article{arqam2026algoinvar,
  title   = {AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA},
  author  = {Arqam, Rehan},
  year    = {2026},
  doi     = {10.5281/zenodo.23627340},
  url     = {https://doi.org/10.5281/zenodo.23627340},
  note    = {Independent Researcher, Islamabad, 44000, Pakistan}
}
```

### Licensing Terms
* **Academic & Non-Commercial Research:** Distributed under the **[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](LICENSE.md)** license.
* **Alternative Licensing Inquiries:** Contact **Rehan Arqam** (`rarqam14@gmail.com`).
