# Step-by-Step Guide: How To Run AlgoInvar

Welcome to the **AlgoInvar** benchmarking repository. This guide provides step-by-step instructions to set up, execute, and reproduce every hardware campaign, multi-width scaling experiment ($n \in \{4, 8, 12, 16, 32, 64\}$), controlled noise sweep, and bitstring post-processing benchmark reported in the manuscript:

> **"AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA"**  
> *Author:* Rehan Arqam (`rarqam14@gmail.com`) — *Independent Researcher, Islamabad*  
> *Permanent DOI:* [https://doi.org/10.5281/zenodo.23627340](https://doi.org/10.5281/zenodo.23627340)

---

## 1. Architectural Overview: How the Codebase is Organized

```text
pro/                                          <-- REPOSITORY ROOT
├── pyproject.toml                            # Standard package configuration & metadata
├── requirements.txt                          # Pinned Python dependencies
├── algoinvar.py                              # Root package bridge for modular namespace resolution
├── README.md                                 # Master project documentation & empirical summary
├── HOW_TO_RUN.md                             # This step-by-step execution guide
├── LICENSE.md                                # Licensing terms (CC BY-NC 4.0)
├── algoinvar research paper/                 # APS PRX Quantum / RevTeX 4.2 manuscript & bibliography
│
├── 01_algoinvar_n4_hardware_baseline/        <-- CAMPAIGN 1: BASELINE (n = 4) & CORE PACKAGE
│   ├── run_ibm_kingston.py                   # Campaign 1 CLI driver (n=4) for 156Q IBM Kingston
│   ├── run_ibm_fez.py                        # Campaign 1 CLI driver (n=4) for 156Q IBM Fez
│   ├── results_kingston/                     # Campaign 1 QPU & simulation data (Job: dbb4hehgv2cc73e7oq40)
│   ├── results_fez/                          # Campaign 1 QPU & simulation data (Job: dbb4ja9gv2cc73e7oue0)
│   ├── __init__.py                           # Package exports ("from algoinvar import run_suite")
│   ├── runner.py                             # Top-level API suite runner
│   ├── benchmarks/                           # Invariant evaluators (VQE particle, QAOA parity & retrace)
│   ├── circuits/                             # Parametric state-preparation circuits
│   ├── hardware/                             # Transpilation & IBM Runtime SamplerV2 integration
│   └── metrics/                              # Statistical estimators, 4-tab Excel & figure exporters
│
├── 02_algoinvar_noise_sweeps_and_mitigation/ <-- CAMPAIGN 2A: CONTROLLED KRAUS NOISE & H2 MITIGATION
│   ├── run_all_experiments.py                # Master script running all 4 noise sweeps & H2 mitigation
│   ├── benchmarking_comparison.json          # Comparative methodology benchmarking record
│   ├── methodology_comparison.xlsx           # Multi-method comparison spreadsheet
│   ├── table_method_comparison.tex           # Publication LaTeX comparison table
│   ├── analysis/                             # Publication vector figure generation
│   ├── circuits/                             # Givens VQE, H2 Hamiltonian, and QAOA circuits
│   ├── results/                              # Raw simulation JSON and 4-tab Excel records
│   └── simulation/                           # Kraus noise channels (T1, T2*, coherent, SPAM)
│
├── 03_algoinvar_multiwidth_register_scaling/ <-- CAMPAIGN 2B: MULTI-WIDTH SCALING (n = 4, 8, 12, 16, 32, 64)
│   ├── HOW_TO_RUN_SCALING.md                 # Dedicated guide for n=4..64 scaling runs
│   ├── qubit_chain_scaling.py                # Calibration-guided greedy DFS chain selector for n=4..64
│   ├── scaling_circuits.py                   # Parametric VQE & QAOA circuit builders for width n
│   ├── scaling_metrics.py                    # 4-tab Excel workbook & vector PDF/PNG figure exporter
│   ├── scaling_runner.py                     # Unified execution engine (Sim, Hardware, Reverification)
│   ├── run_scaling_kingston.py               # Scaling CLI driver for ibm_kingston (Job: dbhkepune4hc73bd3bg0)
│   ├── run_scaling_fez.py                    # Scaling CLI driver for ibm_fez (Job: dbhm1hmne4hc73bd64f0)
│   ├── results_scaling_kingston/             # Verified n=4..64 datasets (245,760 shots, 69.0s QPU time)
│   └── results_scaling_fez/                  # Verified n=4..64 datasets (245,760 shots, 68.0s QPU time)
│
├── 04_algoinvar_cpp_acceleration_engine/     <-- C++17 BITSTRING POST-PROCESSING ENGINE (No Statevector Sim)
│   ├── README.md                             # C++17 POPCNT architecture & pybind11 documentation
│   ├── CMakeLists.txt                        # Standard CMake build configuration (C++17)
│   ├── setup.py                              # Setuptools builder for pybind11 Python extension
│   ├── include/algoinvar_fast.hpp            # FockMetrics, ParityMetrics & 64-bit POPCNT intrinsics
│   ├── src/algoinvar_fast.cpp                # O(S * ceil(n/64)) bitwise Hamming-weight & parity engine
│   ├── src/main.cpp                          # Standalone throughput benchmark on 156Q bitstrings
│   └── bindings/pybind_module.cpp            # pybind11 module bindings for algoinvar_core
│
├── device calibrations/                      # Archived IBM Quantum Calibration Telemetry CSVs
│   ├── Other Experiments/                    # Baseline Campaign 1 calibration snapshots (19 Oct 2026)
│   └── Scaling Experiment 29 Oct/            # Multi-width Campaign 2 calibration snapshots (29 Oct 2026)
└── tests/                                    # Automated unit test suite
```

---

## 2. Environment Setup & Installation

```powershell
# 1. Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install package in editable mode (or via requirements.txt)
pip install -e .
pip install -r requirements.txt
```

---

## 3. Five Ways to Run AlgoInvar

### Workflow 1: Campaign 1 Baseline Drivers ($n = 4$ Qubits, `40,960` Shots)

```powershell
# Mode 1: Local Noiseless Simulation Baseline (0 QPU seconds)
python 01_algoinvar_n4_hardware_baseline/run_ibm_kingston.py
python 01_algoinvar_n4_hardware_baseline/run_ibm_fez.py

# Mode 2: Live IBM Hardware Execution via SamplerV2 (~13.0s QPU time)
python 01_algoinvar_n4_hardware_baseline/run_ibm_kingston.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 01_algoinvar_n4_hardware_baseline/run_ibm_fez.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"

# Mode 3: Offline Reverification of Completed IBM Jobs (0 QPU seconds)
python 01_algoinvar_n4_hardware_baseline/run_ibm_kingston.py --job-id "dbb4hehgv2cc73e7oq40" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 01_algoinvar_n4_hardware_baseline/run_ibm_fez.py --job-id "dbb4ja9gv2cc73e7oue0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
```

---

### Workflow 2: Campaign 2 Multi-Width Register Scaling ($n \in \{4, 8, 12, 16, 32, 64\}$, `245,760` Shots)

Executes all 5 benchmark circuits across six register widths up to $n = 64$ qubits (crossing the 50-qubit classical statevector simulation threshold) in a single 30-circuit batched `SamplerV2` job per processor:

```powershell
# Mode 1: Local Simulation Mode (0 QPU seconds)
python 03_algoinvar_multiwidth_register_scaling/run_scaling_kingston.py
python 03_algoinvar_multiwidth_register_scaling/run_scaling_fez.py

# Mode 2: Live IBM Hardware Execution via SamplerV2 (~68-69s QPU time)
python 03_algoinvar_multiwidth_register_scaling/run_scaling_kingston.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 03_algoinvar_multiwidth_register_scaling/run_scaling_fez.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"

# Mode 3: Offline Reverification of Completed Scaling Jobs (0 QPU seconds)
python 03_algoinvar_multiwidth_register_scaling/run_scaling_kingston.py --job-id "dbhkepune4hc73bd3bg0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python 03_algoinvar_multiwidth_register_scaling/run_scaling_fez.py --job-id "dbhm1hmne4hc73bd64f0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
```
Each run exports a JSON record, a 4-tab Excel workbook (`Executive_Summary`, `VQE_Invariants`, `QAOA_Invariants`, `Hardware_Metadata`), and vector PDF/PNG figures inside `03_algoinvar_multiwidth_register_scaling/results_scaling_<processor>/<mode>/`.

---

### Workflow 3: Controlled Kraus Noise Sweeps & Molecular $\mathrm{H}_2$ Mitigation (`02_algoinvar_noise_sweeps_and_mitigation/`)

```powershell
# Run full controlled noise calibration suite, H2 symmetry post-selection, and figures
python 02_algoinvar_noise_sweeps_and_mitigation/run_all_experiments.py

# Or run individual phases:
python 02_algoinvar_noise_sweeps_and_mitigation/run_all_experiments.py --noise-sweeps
python 02_algoinvar_noise_sweeps_and_mitigation/run_all_experiments.py --mitigation
python 02_algoinvar_noise_sweeps_and_mitigation/run_all_experiments.py --comparison
python 02_algoinvar_noise_sweeps_and_mitigation/run_all_experiments.py --plots
```

---

### Workflow 4: C++17 Hardware-`POPCNT` Bitstring Post-Processing Engine (`04_algoinvar_cpp_acceleration_engine/`)

> **Why `04_algoinvar_cpp_acceleration_engine/` is in the repository:** The `04_algoinvar_cpp_acceleration_engine/` module does **not** perform quantum statevector simulation. Instead, it implements the $O(S \cdot \lceil n/64 \rceil)$ classical bitstring post-processing step (evaluating Hamming weights $\text{wt}(x)$ and parity eigenvalues $(-1)^{\sum y_j}$ on wide 64- to 156-qubit hardware bitstrings) using 64-bit CPU `POPCNT` intrinsics (`__popcnt64` / `__builtin_popcountll`) with `pybind11` bindings (`algoinvar_core`).

```powershell
cd 04_algoinvar_cpp_acceleration_engine
g++ -O3 -std=c++17 src/main.cpp src/algoinvar_fast.cpp -o algoinvar_bench
./algoinvar_bench
```

---

### Workflow 5: Python Library API & Automated Unit Tests

```powershell
# Run automated unit tests for exact algebraic commutation & invariant conservation
python -m unittest tests/test_invariants.py
```
