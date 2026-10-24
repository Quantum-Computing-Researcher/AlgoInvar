# Step-by-Step Guide: How To Run This

Welcome to the **AlgoInvar** benchmarking repository. This guide provides comprehensive, step-by-step instructions for researchers, quantum software engineers, and auditors to set up, execute, and reproduce every benchmark and experiment reported in the manuscript:

> **"AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA"**  
> *Author:* Rehan Arqam (`rarqam14@gmail.com`) — *Independent Researcher, Islamabad*  
> *Permanent DOI:* [https://doi.org/10.5281/zenodo.23627340](https://doi.org/10.5281/zenodo.23627340)

---

## 1. Architectural Overview: How the Codebase is Organized

The repository follows modern Python packaging standards (PEP 517 / PEP 621):

```
pro/                                 <-- REPOSITORY ROOT
├── pyproject.toml                   # Standard package configuration & metadata
├── requirements.txt                 # Pinned dependencies
├── README.md                        # Master project documentation & commercial analysis
├── HOW_TO_RUN.md                    # This step-by-step execution guide
├── run_ibm_kingston.py              # Master CLI driver for 156Q IBM Kingston (Heron r2)
├── run_ibm_fez.py                   # Master CLI driver for 156Q IBM Fez (Heron r2)
│
├── algoinvar/                       <-- PYTHON LIBRARY PACKAGE (Core API)
│   ├── __init__.py                  # Package exports (enables "from algoinvar import run_suite")
│   ├── runner.py                    # Top-level API suite runner (run_suite entry point)
│   ├── benchmarks/                  # Invariant implementations (VQE particle, QAOA parity & retrace)
│   ├── circuits/                    # Parametric state-preparation circuits
│   ├── hardware/                    # Transpilation & IBM Runtime primitive integration
│   └── metrics/                     # Exact statistical estimators & sub-Poissonian variance
│
├── cpp/                         <-- HIGH-PERFORMANCE C++ CORE (Hardware POPCNT & Bitwise Engine)
│   ├── CMakeLists.txt           # Standard CMake build configuration (C++17/20)
│   ├── setup.py                 # Setuptools builder for pybind11 Python extension
│   ├── include/                 # Header declarations: FockMetrics & ParityMetrics
│   ├── src/                     # Low-latency bitwise evaluation engine (CPU POPCNT)
│   └── bindings/                # pybind11 module bindings for algoinvar_core
│
├── algoinvar_2ndexp/                <-- CONTROLLED NOISE SIMULATION EXPERIMENTS
│   ├── run_all_experiments.py       # Master script running all 5 simulation sweeps
│   ├── analysis/                    # Statistical aggregation & table generation
│   ├── circuits/                    # Controlled noise channel circuits
│   ├── figures/                     # TikZ vector plots and generated visuals
│   ├── results/                     # Raw simulation JSON and CSV records
│   └── simulation/                  # Kraus noise models (Phase damping, Bit-flip, Depolarizing)
│
├── examples/                        # Standalone educational demonstrations
│   └── demo_noise_sweep.py          # Fast noise sweep demo
│
├── tests/                           # Automated unit test suite
│   └── test_invariants.py           # Verification of exact algebraic invariants
│
├── results_kingston/                # Physical IBM Kingston QPU and simulation benchmark data
├── results_fez/                     # Physical IBM Fez QPU and simulation benchmark data
└── device calibrations/             # Hardware calibration datasets and snapshot properties
```

### Package Architecture & Clean API Design
The core benchmarking framework is organized as a modular Python package inside `algoinvar/`. It exposes a clean, top-level interface through the main runner:

```python
from algoinvar import run_suite
```

The runner coordinates the entire benchmarking pipeline: it compiles the invariant circuits, submits them to the designated backend (simulator or real hardware), calculates exact expectation values and sub-Poissonian number variances, and reports subspace leakage and parity preservation without requiring low-level circuit plumbing from the user.

---

## 2. Environment Setup & Installation

### Step 2.1: Clone or Open the Repository
Clone the repository from GitHub or open your project folder:
```bash
git clone https://github.com/Quantum-Computing-Researcher/AlgoInvar.git
cd AlgoInvar
```

### Step 2.2: Create and Activate a Virtual Environment (Recommended)
Using an isolated virtual environment prevents library version conflicts:

* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 2.3: Install Dependencies and AlgoInvar in Editable Mode
Run either of the following commands from the repository root:

* **Option A: Install in editable development mode (Recommended):**
  ```bash
  pip install -e .
  ```
  *This reads `pyproject.toml` and links the `algoinvar` package directly into your Python environment.*

* **Option B: Install via `requirements.txt`:**
  ```bash
  pip install -r requirements.txt
  ```

---

## 3. Four Ways to Run AlgoInvar

Researchers can interact with the framework through four primary workflows:

```
Researcher
   │
   ├── Workflow 1: Python Library API (Jupyter / Custom Scripts)
   ├── Workflow 2: Command Line Drivers (IBM Kingston & Fez Baselines)
   ├── Workflow 3: Master Simulation Experiments (Controlled Noise Sweeps)
   └── Workflow 4: Unit Testing & Integrity Verification
```

---

### Workflow 1: Using `algoinvar` as a Python Library (Jupyter / Scripts)

This is the standard programmatic workflow for integrating invariant checking into quantum algorithms or variational loops.

Create a new Python file (e.g. `test_suite.py`) or open a Jupyter Notebook, and run:

```python
from algoinvar import run_suite
from qiskit_aer import AerSimulator

# 1. Select any backend (AerSimulator or a real IBM QPU backend)
backend = AerSimulator()

# 2. Execute the complete AlgoInvar suite with high-precision statistics
report = run_suite(
    backend=backend,
    num_qubits=4,       # System size
    shots=4096,         # Measurement shots per invariant circuit
    vqe_particles=2,    # Targeted electron count N_e
    vqe_layers=2,       # Givens rotation depth
    qaoa_depth=2        # QAOA layer depth p
)

# 3. Print the formatted benchmark report
print(report.summary())
```

#### What `run_suite` measures automatically:
1. **VQE Particle Conservation:**
   - Evaluates $\langle \hat{N} \rangle = \sum_{k=0}^{n-1} \frac{1 - \langle Z_k \rangle}{2}$.
   - Verifies sub-Poissonian number variance $\text{Var}(\hat{N}) = 0$.
   - Computes Fock subspace leakage $\mathcal{L}_{\mathrm{Fock}} = 1 - P(N = N_e)$.
2. **QAOA Global $\mathbb{Z}_2$ Parity:**
   - Evaluates the transversal stabilizer $\langle \hat{P}_X \rangle = \langle \bigotimes_{k=0}^{n-1} X_k \rangle \equiv +1$.
   - Detects phase-flip ($Z$) errors that commute with the problem Hamiltonian but anticommute with the mixer.
3. **QAOA Retrace Echo:**
   - Applies the forward-reverse sequence $U_{\text{QAOA}}^\dagger U_{\text{QAOA}}$ from $|+\rangle^{\otimes n}$.
   - Measures return fidelity $F_{\text{echo}} = |\langle +^{\otimes n} | \psi \rangle|^2 \equiv 1.0$.

---

### Workflow 2: Running the Ready-Made IBM QPU & Baseline Drivers (CLI)

The repository provides two master command-line drivers located in the root directory:
* [`run_ibm_kingston.py`](run_ibm_kingston.py) — 156-qubit IBM Kingston (Heron r2 processor)
* [`run_ibm_fez.py`](run_ibm_fez.py) — 156-qubit IBM Fez (Heron r2 processor)

#### Mode A: Local Noiseless Simulation Baseline (No IBM Account Needed)
Run directly from your terminal:
```bash
python run_ibm_kingston.py
```
or
```bash
python run_ibm_fez.py
```
**Expected Behavior:**
- Evaluates the circuits on a local noiseless `AerSimulator`.
- Prints a structured comparison table showing Theory vs Measured values.
- Exports structured results to `results_kingston/simulation/` or `results_fez/simulation/`.

#### Mode B: Physical Hardware Execution on IBM Quantum (156Q Heron r2)
If you have an IBM Quantum Cloud API token and CRN:
```bash
python run_ibm_kingston.py --hardware --token "YOUR_IBM_QUANTUM_TOKEN" --crn "YOUR_IBM_CLOUD_CRN"
```
**Execution Guardrails:**
- Circuit transpilation is mapped to the optimal 4-qubit linear chain with native 2-qubit CZ gates.
- Runtime is protected by an execution budget safeguard (`BUDGET_S = 180.0s`).
- Raw measurement counts, transpiled circuit metrics, and invariant evaluations are saved to `results_kingston/hardware_run/`.

#### Mode C: Offline Job Re-Verification (0 QPU Seconds Consumed)
If an IBM hardware job has already run, you can re-fetch and audit the results without consuming any quantum compute time:
```bash
python run_ibm_kingston.py --job-id "YOUR_COMPLETED_JOB_ID" --token "YOUR_IBM_QUANTUM_TOKEN"
```

---

### Workflow 3: Running Experiment 2 (Controlled Noise Sweeps & Simulation Suite)

The directory [`algoinvar_2ndexp/`](algoinvar_2ndexp/) contains the complete codebase for **Experiment 2**, which evaluates algorithmic invariants under controlled physical noise channels and benchmarks symmetry-filtered error mitigation for molecular chemistry.

```
algoinvar_2ndexp/
├── run_all_experiments.py       # Master driver with modular CLI flags
├── analysis/
│   └── plot_noise_calibration.py# Generates 300 DPI publication plots (Fig 4 & Fig 5)
├── circuits/
│   ├── qaoa_maxcut.py           # QAOA circuits & retrace echo sequences (p=1, 2)
│   └── vqe_givens.py            # Givens-rotation VQE circuits & H2 Hamiltonian
├── figures/                     # Final exported figures copied for publication
├── results/
│   ├── device_calibration/      # Protocol comparison table (LaTeX)
│   ├── error_injection/         # Sweep datasets (JSON & Excel) for AD, PD, Coherent, SPAM
│   ├── figures/                 # Generated PDF and PNG vector plots
│   └── symmetry_mitigation/     # Molecular H2 raw vs post-selected energy records
└── simulation/
    ├── error_injection.py       # Kraus error channels (T1, T2, coherent drift, readout)
    ├── symmetry_mitigation.py   # H2 ground state energy with Hamming weight w=2 filtering
    └── benchmarking_comparison.py# Classical tax comparison: Clifford RB, XEB, QST vs AlgoInvar
```

---

#### 3.1: Running the Complete Experiment 2 (All Sweeps, Mitigation & Figures)

From the project root (`pro/`), run the master experiment runner:

```bash
python algoinvar_2ndexp/run_all_experiments.py
```

* **Default configuration:** Runs all 4 sub-experiments with high statistical precision ($S = 50,000$ shots per circuit).
* **Execution time:** Approximately 1–2 minutes on modern multi-core CPUs.

> [!TIP]
> **Fast Smoke-Test Execution:**
> For quick local verification or testing without waiting for 50,000 shots, pass a smaller shot budget via `--shots`:
> ```bash
> python algoinvar_2ndexp/run_all_experiments.py --shots 2048
> ```

---

#### 3.2: Running Individual Sub-Experiments in Experiment 2

You can run individual phases of Experiment 2 using dedicated command-line flags:

##### Sub-Experiment 2A: Controlled Noise Channel Sweeps (`--noise-sweeps`)
Simulates 4 distinct physical noise channels across parameter grids to test invariant sensitivity:
```bash
python algoinvar_2ndexp/run_all_experiments.py --noise-sweeps
```
* **Physics Evaluated:**
  1. **Amplitude Damping ($T_1$ decay, $\gamma \in [0.0, 0.20]$):**
     Monitors particle decay $|1\rangle \to |0\rangle$. Demonstrates that $\langle \hat{N} \rangle$ collapses toward 0, and the particle asymmetry ratio $R_{\mathrm{asym}} = P(w=1)/P(w=3) \to \infty$ uniquely fingerprinting $T_1$ relaxation.
  2. **Pure Dephasing ($T_2$ decoherence, $\lambda \in [0.0, 0.25]$):**
     Applies Kraus operators $K_0 = \begin{pmatrix}1&0\\0&\sqrt{1-\lambda}\end{pmatrix}, K_1 = \begin{pmatrix}0&0\\0&\sqrt{\lambda}\end{pmatrix}$.
     Confirms that VQE particle number is strictly preserved ($\langle \hat{N} \rangle = 2.0113 \pm 0.0018$ at $\lambda=0.25$, with shift caused by gate dephasing in compiled Givens gates), while QAOA global parity collapses from $1.0000 \to 0.1026 \pm 0.0044$ ($p=1$) and $0.0173 \pm 0.0045$ ($p=2$).
  3. **Coherent Overrotation ($\epsilon_\theta \in [-0.15\pi, +0.15\pi]$):**
     Demonstrates quadratic Fock leakage scaling as $\mathcal{O}(\epsilon^2)$ while maintaining symmetric single-particle populations ($R_{\mathrm{asym}} \approx 1.0$).
  4. **SPAM Readout Confusion ($\epsilon_{\text{meas}} \in [0.0, 0.08]$):**
     Evaluates symmetric bit-flip noise on detector readout.
* **Outputs Generated:**
  - `algoinvar_2ndexp/results/error_injection/amplitude_damping_sweep.json`
  - `algoinvar_2ndexp/results/error_injection/phase_dephasing_sweep.json`
  - `algoinvar_2ndexp/results/error_injection/coherent_overrotation_sweep.json`
  - `algoinvar_2ndexp/results/error_injection/spam_confusion_sweep.json`
  - `algoinvar_2ndexp/results/error_injection/noise_injection_results.xlsx` (Multi-sheet Excel workbook)

##### Sub-Experiment 2B: Molecular $\mathrm{H}_2$ VQE Symmetry Post-Selection (`--mitigation`)
Benchmarks symmetry-filtered error mitigation on molecular hydrogen ($\mathrm{H}_2$ at $R = 0.735\ \text{\AA}$ in the STO-3G basis mapped to 4 qubits):
```bash
python algoinvar_2ndexp/run_all_experiments.py --mitigation
```
* **Physics Evaluated:**
  - Sweeps composite noise scaling factors from $0.0\times$ to $2.0\times$.
  - Measures the raw ground-state energy versus the symmetry-filtered energy obtained by post-selecting strictly on shots in the two-electron subspace ($w=2$).
  - **Result:** Post-selection suppresses ground-state energy error from $520.6\ \text{mHa}$ down to $369.6\ \text{mHa}$ at scale $2.0$ (a $29.0\%$ error reduction) while highlighting the sampling throughput penalty (retained shot fraction drops from $100\%$ to $13.5\%$).
* **Outputs Generated:**
  - `algoinvar_2ndexp/results/symmetry_mitigation/h2_vqe_mitigation_data.json`
  - `algoinvar_2ndexp/results/symmetry_mitigation/symmetry_mitigation_results.xlsx`

##### Sub-Experiment 2C: Benchmarking Protocol Classical Overhead Comparison (`--comparison`)
Generates the comparative analysis table contrasting AlgoInvar against Clifford Randomized Benchmarking (RB), Cross-Entropy Benchmarking (XEB), and Quantum State Tomography (QST):
```bash
python algoinvar_2ndexp/run_all_experiments.py --comparison
```
* **Outputs Generated:**
  - `algoinvar_2ndexp/results/device_calibration/table_method_comparison.tex` (Ready-to-embed LaTeX table)
  - `algoinvar_2ndexp/results/device_calibration/benchmarking_comparison.xlsx`

##### Sub-Experiment 2D: Regenerating Publication Figures (`--plots`)
Renders all publication-ready vector figures from the generated simulation data:
```bash
python algoinvar_2ndexp/run_all_experiments.py --plots
```
* **Outputs Generated:**
  - **Figure 4:** 4-panel calibration curves (`fig4_noise_calibration.png` and `fig4_noise_calibration.pdf`)
  - **Figure 5:** $\mathrm{H}_2$ molecular energy mitigation curves (`fig5_energy_mitigation.png` and `fig5_energy_mitigation.pdf`)
  - Copies all generated figures to both `algoinvar_2ndexp/results/figures/` and `algoinvar_2ndexp/figures/`.

---

### Workflow 4: Educational Demo & Automated Unit Tests

#### Fast Noise Sensitivity Demo
To see an immediate side-by-side demonstration of how increasing depolarizing noise increases $\text{Var}(\hat{N})$, increases subspace leakage, and degrades global parity:
```bash
python examples/demo_noise_sweep.py
```

#### Automated Unit Test Suite
To verify that all mathematical invariants hold analytically under noiseless execution:
```bash
python -m unittest tests/test_invariants.py
```
**Expected Output:**
```text
....
----------------------------------------------------------------------
Ran 4 tests in 13.839s

OK
```

---

## 4. Practical Notes & Configuration

* **Local Simulation vs. Hardware Access:** An IBM Quantum hardware account is not required to run or reproduce any of the experiments. All simulation baselines (`run_ibm_kingston.py`, `run_ibm_fez.py`, and `algoinvar_2ndexp/run_all_experiments.py`) execute locally on your machine via Qiskit AerSimulator. Hardware credentials are only needed if submitting jobs to physical Heron QPUs.
* **Customizing Circuit Parameters:** In Python, you can adjust system parameters directly in the call: `run_suite(num_qubits=6, shots=8192)`. For terminal CLI runs, parameters like qubit chain length (`N_QUBITS`) and shot counts (`SHOTS`) are configured near the top of `run_ibm_kingston.py` and `run_ibm_fez.py`.
* **Repository Hygiene:** The project includes a pre-configured `.gitignore` that handles Python build artifacts, virtual environments, and bytecode caches automatically.

---

## 5. Citation

If you use AlgoInvar in your research, please cite:

```bibtex
@article{arqam2026algoinvar,
  title   = {AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA},
  author  = {Arqam, Rehan},
  year    = {2026},
  url     = {https://github.com/Quantum-Computing-Researcher/AlgoInvar},
  note    = {Independent Researcher, Islamabad}
}
```
