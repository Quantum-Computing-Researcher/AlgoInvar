# AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA

[<img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23627340.svg" height="20" alt="DOI: 10.5281/zenodo.23627340">](https://doi.org/10.5281/zenodo.23627340) [<img src="https://img.shields.io/badge/Guide-How%20To%20Run-teal.svg" height="20" alt="Guide: How To Run">](HOW_TO_RUN.md) [<img src="https://img.shields.io/badge/License-PolyForm%20Noncommercial-blue.svg" height="20" alt="License: PolyForm Noncommercial 1.0.0">](LICENSE.md) [<img src="https://img.shields.io/badge/Commercial-Royalty%20Agreement-orange.svg" height="20" alt="Commercial License">](LICENSE.md) [<img src="https://img.shields.io/badge/Python-3.9+-green.svg" height="20" alt="Python 3.9+">](https://www.python.org/downloads/) [<img src="https://img.shields.io/badge/Qiskit-1.0+-613394.svg" height="20" alt="Qiskit 1.0+">](https://qiskit.org/)

> 📖 **Quick Start:** For step-by-step installation, Python API usage, IBM hardware execution, and Experiment 2 reproduction guides, see [**HOW_TO_RUN.md**](HOW_TO_RUN.md).

**AlgoInvar** is an in situ, simulation-free, parameter-free quantum hardware benchmarking and characterization framework anchored to exact algebraic conservation laws and continuous physical symmetries in algorithmically relevant workloads: **Variational Quantum Eigensolver (VQE)** fermionic chemistry and the **Quantum Approximate Optimization Algorithm (QAOA)** combinatorial optimization.

Validated on dual 156-qubit IBM Heron r2 utility-era processors (`ibm_kingston` and `ibm_fez`), AlgoInvar executes **40,960 physical shots per system across 5 batched ISA circuits in exactly 13.0 seconds of QPU runtime**, providing physics-informed error channel diagnostics with $O(1)$ classical theoretical complexity and zero tensor-network simulation.

---

## 💼 Commercial Importance & Enterprise Value

As quantum computing transitions from laboratory experiments to commercial enterprise cloud deployments, hardware evaluation faces steep financial, computational, and operational bottlenecks. AlgoInvar addresses these challenges directly:

### 1. Drastic Cloud QPU Cost Reduction (13.0s Execution Time)
* **The Problem:** Commercial quantum cloud providers (IBM Quantum, AWS Braket, Azure Quantum, Google Quantum AI) bill users by execution seconds, circuit evaluations, or shot volume. Standard characterization methods such as Quantum State Tomography (QST), multi-seed Randomized Benchmarking (RB), or Cross-Entropy Benchmarking (XEB) require hundreds of separate circuit submissions running for hours or days, costing enterprises tens of thousands of dollars per calibration cycle.
* **The AlgoInvar Advantage:** Through single-job Instruction Set Architecture (ISA) batching via Qiskit Runtime SamplerV2, AlgoInvar evaluates 5 algorithmically structured circuits with 8,192 shots per circuit ($40,960$ physical shots total) in **exactly 13.0 seconds of billable QPU time**. This delivers an enterprise-grade hardware assessment at a tiny fraction of conventional cloud computing costs.

### 2. Zero Classical Supercomputing & HPC Overhead ($O(1)$ Reference Derivation)
* **The Problem:** Holistic fidelity benchmarks such as Cross-Entropy Benchmarking (XEB) and Quantum Volume (QV) rely on comparing measured sample frequencies against classically simulated ideal output distributions. Beyond 50 qubits, calculating exact statevectors requires multi-GPU supercomputers and high-performance computing (HPC) cluster allocations, which becomes completely intractable beyond 70 qubits.
* **The AlgoInvar Advantage:** Reference invariant values in AlgoInvar ($\langle \hat{N} \rangle \equiv N_e$, $\text{Var}(\hat{N}) \equiv 0$, $\langle \hat{\mathcal{P}} \rangle \equiv +1$) are exact algebraic conservation theorems known analytically *a priori*. Deriving the theoretical reference requires **$O(1)$ classical compute**, followed by lightweight linear $O(S \cdot n)$ bitstring post-processing. Enterprise clients can verify 4 qubits, 156 qubits, or 10,000 qubits without spending a single dollar on classical supercomputing time.

### 3. Enterprise Pre-Flight Verification & Dynamic Workload Routing
* **The Problem:** In production quantum SaaS environments (e.g., pharmaceutical molecular simulations, materials discovery, financial portfolio optimization), variational algorithms submit complex parameterized circuits requiring days of hybrid optimization. If an assigned QPU partition suffers from elevated $T_1$ thermal relaxation, readout assignment bias, or entangling gate crosstalk, the entire multi-thousand-dollar business workflow produces corrupt, non-convergent results.
* **The AlgoInvar Advantage:** AlgoInvar acts as an automated, simulation-free **"pre-flight health-check"**. Prior to dispatching a high-value variational workload, a 13-second AlgoInvar sweep queries the QPU. If out-of-sector leakage $\mathcal{L}_{\mathrm{leak}}$ or directional asymmetry $R_{\mathrm{asym}}$ exceeds enterprise tolerance, middleware dynamically routes the job to a healthier physical sub-chain or alternative processor, protecting enterprise clients from wasted budgets and flawed data.

### 4. Vendor-Neutral SLA Verification & Hardware Auditing
* **The Problem:** Enterprise clients procuring dedicated quantum hardware access need objective, hardware-agnostic criteria to verify that service level agreements (SLAs) and advertised gate fidelities translate into actual algorithmic circuit fidelity.
* **The AlgoInvar Advantage:** Because algebraic invariants are dictated by algorithm mathematics rather than transmon-specific calibration conventions, AlgoInvar provides a vendor-neutral auditing standard applicable across superconducting, trapped-ion, photonic, and neutral-atom architectures.

### 5. Intellectual Property & Commercial Licensing
AlgoInvar is distributed under a clear dual-licensing structure:
* **Academic & Non-Commercial Research:** Freely accessible and royalty-free under the **PolyForm Noncommercial License 1.0.0** for educational, academic, and scientific evaluations.
* **Commercial Hardware & Cloud Deployments:** Enterprise integration into commercial quantum computer operating stacks, cloud benchmarking dashboards, automated calibration firmware, or proprietary SaaS platforms is governed by formal commercial licensing terms. Inquiries: `rarqam14@gmail.com`.

---

## 📁 Repository Directory Structure & File Inventory

The repository is organized into distinct modules separating hardware execution, modular benchmarking libraries, controlled simulation experiments, and the scientific manuscript:

```
AlgoInvar/
├── README.md                    # Comprehensive master repository documentation
├── HOW_TO_RUN.md                # Step-by-step execution guide for all workflows & Exp 2
├── LICENSE.md                   # Dual-licensing terms (PolyForm Noncommercial 1.0.0)
├── pyproject.toml               # Python project configuration and package metadata
├── requirements.txt             # Python dependencies (Qiskit 1.0+, NumPy, Pandas, Matplotlib)
│
├── run_ibm_kingston.py          # Master execution driver for 156Q IBM Kingston (Heron r2)
├── run_ibm_fez.py               # Master execution driver for 156Q IBM Fez (Heron r2)
│
├── algoinvar/                   # Core AlgoInvar Python Library Package
│   ├── benchmarks/              # Algebraic invariant evaluators
│   │   ├── base.py              # Base abstract class for invariant benchmark protocols
│   │   ├── vqe_invariants.py    # Fock-space particle-number expectation, variance & leakage
│   │   └── qaoa_invariants.py   # Global Z2 parity invariance & echo metrics
│   ├── circuits/                # Quantum circuit generators
│   │   ├── vqe_ansatz.py        # Excitation-preserving Givens rotation networks
│   │   └── qaoa_ansatz.py       # Max-Cut alternating ansatz with X-basis readout
│   ├── hardware/                # Hardware execution & compilation middleware
│   │   ├── backend_router.py    # IBM Quantum Cloud credentials & service initializers
│   │   ├── subgraph_search.py   # Calibration-guided greedy chain optimization
│   │   └── sampler_v2_executor.py # Single-job batched ISA payload builder (SamplerV2)
│   └── metrics/                 # Statistical error analysis & uncertainty propagation
│       ├── fock_metrics.py      # Hamming weight moments & sector distributions
│       ├── parity_metrics.py    # Dichotomy expectation & multi-layer parity tracking
│       └── uncertainty.py       # Binomial and multinomial standard error propagation
│
├── cpp/                         # High-Performance C++ Core Engine (Native bitwise accelerator)
│   ├── README.md                # C++ architecture, hardware intrinsics & benchmark guide
│   ├── CMakeLists.txt           # Standard CMake build configuration (C++17/20)
│   ├── setup.py                 # Setuptools builder for pybind11 Python extension
│   ├── include/
│   │   └── algoinvar_fast.hpp   # Header definitions: FockMetrics, ParityMetrics & prototypes
│   ├── src/
│   │   ├── algoinvar_fast.cpp   # Bitwise evaluation engine & moment accumulators (CPU POPCNT)
│   │   └── main.cpp             # Standalone benchmark executable for large-scale payloads
│   └── bindings/
│       └── pybind_module.cpp    # pybind11 module bindings for algoinvar_core
│
├── algoinvar_2ndexp/            # Controlled Simulation Experiments & Mitigation Suite
│   ├── README.md                # Sub-directory guide for simulation suite
│   ├── run_all_experiments.py   # Unified CLI runner for noise sweeps, mitigation & plots
│   ├── circuits/                # Experiment circuit definitions
│   │   ├── vqe_givens.py        # 4-qubit Givens networks and H2 molecular Hamiltonian
│   │   └── qaoa_maxcut.py       # 4-qubit ring-topology QAOA Max-Cut circuits
│   ├── simulation/              # Parameterized Kraus noise sweeps & error mitigation
│   │   ├── error_injection.py   # 4-channel noise sweeps (T1, T2*, coherent, SPAM)
│   │   ├── symmetry_mitigation.py # Molecular H2 VQE symmetry-based post-selection
│   │   └── benchmarking_comparison.py # Comparative resource-overhead taxonomy
│   ├── analysis/                # Vector figure generation
│   │   └── plot_noise_calibration.py # Generates noise sweep and mitigation vector plots
│   └── results/                 # Raw experimental outputs, JSON records & multi-tab Excel workbooks
│       ├── error_injection/     # JSON & XLSX records for all 4 noise channels
│       ├── symmetry_mitigation/ # JSON & XLSX records for molecular H2 post-selection
│       ├── device_calibration/  # Cross-protocol taxonomy comparisons and LaTeX tables
│       └── figures/             # High-resolution PNG and PDF vector plot exports
│
├── results_kingston/            # Empirical Datasets: ibm_kingston (156Q Heron r2)
│   ├── hardware_run/            # Live QPU execution outputs (Job ID: dbb4hehgv2cc73e7oq40)
│   │   ├── ibm_kingston_results.json  # Raw measurement counts (40,960 shots)
│   │   ├── ibm_kingston_results.xlsx  # Multi-sheet statistical diagnostics workbook
│   │   └── figures/             # Native vector plots for Kingston (Figures 1 & 2)
│   ├── simulation/              # Ideal AerSimulator noiseless baseline
│   └── reverification/          # Offline post-processing and calibration verification
│
├── results_fez/                 # Empirical Datasets: ibm_fez (156Q Heron r2)
│   ├── hardware_run/            # Live QPU execution outputs (Job ID: dbb4ja9gv2cc73e7oue0)
│   │   ├── ibm_fez_results.json       # Raw measurement counts (40,960 shots)
│   │   ├── ibm_fez_results.xlsx       # Multi-sheet statistical diagnostics workbook
│   │   └── figures/             # Native vector plots for Fez (Figures 1 & 2)
│   ├── simulation/              # Ideal AerSimulator noiseless baseline
│   └── reverification/          # Offline post-processing and calibration verification
│
├── device calibrations/         # Raw hardware calibration snapshots from IBM Quantum
├── examples/                    # Standalone Jupyter / Python demonstration workflows
└── tests/                       # Unit testing suite
    └── test_invariants.py       # Unit tests for algebraic commutation and invariant evaluators
```

---

## 🔬 Mathematical Invariants & Theoretical Foundations

AlgoInvar formulates three foundational classes of exact mathematical invariants that govern structured quantum algorithms:

### 1. VQE Particle-Number Sector Invariant
In fermionic molecular quantum chemistry mapped via the Jordan-Wigner transformation, the total particle-number operator is diagonal in the computational basis:
$$\hat{N} = \sum_{j=1}^n \frac{I - Z_j}{2}$$

A two-qubit Givens rotation $G_{ij}(\theta) = \exp\left[-i \frac{\theta}{4} g_{ij}\right]$ is generated by the planar excitation Hamiltonian $g_{ij} = X_i X_j + Y_i Y_j$. Because the generator strictly commutes with local particle number ($[g_{ij}, Z_i + Z_j] = 0$), the exponentiated unitary gate satisfies:
$$[G_{ij}(\theta), \hat{N}] = 0 \quad \forall \theta \in \mathbb{R}$$

**Theorem 1:** For any arbitrary-depth Givens network $U_{\text{VQE}}(\vec{\theta}) = \prod_k G_{i_k j_k}(\theta_k)$ initialized in an $N_e$-electron Hartree-Fock reference state $|\psi_0\rangle$:
$$\langle \hat{N} \rangle \equiv N_e \quad \text{and} \quad \text{Var}(\hat{N}) \equiv 0 \quad \forall \vec{\theta} \in \mathbb{R}^M$$

* **Measurement:** Read directly in the computational $Z$-basis. Every bitstring $x \in \{0, 1\}^n$ is an eigenstate of $\hat{N}$ with eigenvalue equal to its Hamming weight $w(x) = \sum x_j$.
* **Sector Leakage Metric:** The total probability mass outside the target $N_e$ sector:
$$\mathcal{L}_{\mathrm{leak}} = 1 - \sum_{x:\, w(x)=N_e} \frac{C(x)}{S}$$

### 2. QAOA Global $\mathbb{Z}_2$ Parity Invariant
In the Quantum Approximate Optimization Algorithm for graph partitioning (Max-Cut) on an arbitrary graph $G = (V, E)$, the depth-$p$ state is prepared from $|+\rangle^{\otimes n}$ via alternating cost ($H_C = \frac{1}{2}\sum_{(u,v)} (I - Z_u Z_v)$) and mixer ($H_B = \sum_u X_u$) unitaries.

We define the global parity observable as the collective $X$-spin:
$$\hat{\mathcal{P}} = \bigotimes_{u \in V} X_u$$

**Theorem 2:** Because $[\hat{\mathcal{P}}, H_B] = 0$ and $[\hat{\mathcal{P}}, Z_u Z_v] = 0$ for all graph edges, $[\hat{\mathcal{P}}, U_{\text{QAOA}}] = 0$. Consequently:
$$\langle \hat{\mathcal{P}} \rangle \equiv +1.0 \quad \forall p \ge 1, \quad \forall (\vec{\gamma}, \vec{\beta}) \in \mathbb{R}^{2p}, \quad \forall G$$

* **Measurement:** Read directly in the transversal $X$-basis by applying local Hadamard gates $H^{\otimes n}$ prior to readout.
* **Diagnostic Power:** Pauli-$Z$ phase errors and $Y$ errors anticommute with $\hat{\mathcal{P}}$ ($\{Z_u, \hat{\mathcal{P}}\} = 0$), inverting the parity eigenvalue. Global parity decay across layers $p$ selectively quantifies the accumulation of multi-qubit entangling phase dephasing.

### 3. Unitary Retrace Echo Benchmarking
Appends the inverse circuit $U^\dagger$ to the forward unitary $U$, measuring return probability to the reference state:
$$F_{\text{echo}} = |\langle \psi_0 | U^\dagger U | \psi_0 \rangle|^2 \equiv 1.0$$
* **Diagnostic Complementarity:** In-manifold coherent rotation errors $\theta \to \theta + \delta$ strictly preserve forward sector conservation ($\text{Var}(\hat{N}) \equiv 0$), but cause a quadratic drop in echo fidelity $F_{\text{echo}} \propto \cos^2(\delta)$.
* **Scope & Caveat:** While echo sequences detect in-manifold implementation errors that preserve the target sector, they do not universally decouple coherent errors from dissipation, as static systematic errors can in certain symmetric instances partially refocus or cancel during forward-reverse sequences.

---

## 📊 Empirical Validation on 156-Qubit IBM Heron r2 Hardware

AlgoInvar was physically validated on two independent 156-qubit IBM Heron r2 superconducting processors accessed via the IBM Quantum Platform:
* **`ibm_kingston` (Heron r2):** Calibration-selected sub-chain $[50, 49, 48, 47]$ (Mean $\bar{\epsilon}_{\text{CZ}} = 0.194\%$, $T_1 = 272.3\ \mu\text{s}$, $T_2 = 169.6\ \mu\text{s}$). Job ID: `dbb4hehgv2cc73e7oq40`.
* **`ibm_fez` (Heron r2):** Calibration-selected sub-chain $[109, 110, 111, 98]$ (Mean $\bar{\epsilon}_{\text{CZ}} = 0.215\%$, $T_1 = 146.8\ \mu\text{s}$, $T_2 = 71.2\ \mu\text{s}$). Job ID: `dbb4ja9gv2cc73e7oue0`.

Each hardware execution batched 5 native ISA circuits ($8,192$ shots per circuit, **$40,960$ physical shots total**) completed in **exactly 13.0 seconds of physical QPU runtime**:

### Master Hardware Results Table

| Circuit Setting / Invariant | Exact Theory | Noiseless Aer | `ibm_kingston` (Heron r2) | `ibm_fez` (Heron r2) | Physical Error Diagnosis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **VQE Fermionic Chemistry ($L=2$):** | | | | | |
| Particle Expectation $\langle \hat{N} \rangle$ | $2.0000$ | $2.0000$ | $1.9760 \pm 0.0040$ | $1.9403 \pm 0.0044$ | Thermal relaxation ($T_1$) asymmetry ($\langle \hat{N} \rangle < N_e$) |
| Particle Variance $\text{Var}(\hat{N})$ | $0.0000$ | $0.0000$ | $0.1289 \pm 0.0060$ | $0.1616 \pm 0.0062$ | Excitation-changing gate infidelities & SPAM |
| In-Sector Population ($N_e=2$) | $1.0000$ | $1.0000$ | $0.9163 \pm 0.0031$ | $0.8839 \pm 0.0035$ | Preserved computational target subspace |
| Out-of-Sector Leakage $\mathcal{L}_{\mathrm{leak}}$ | $0.0000$ | $0.0000$ | $8.37\% \pm 0.31\%$ | $11.61\% \pm 0.35\%$ | Non-unitary population loss into unphysical sectors |
| Retrace Echo Fidelity $F_{\text{echo}}$ | $1.0000$ | $1.0000$ | $0.8083 \pm 0.0043$ | $0.8013 \pm 0.0044$ | Round-trip unitary degradation & coherent drift |
| **QAOA Max-Cut Graph ($n=4$):** | | | | | |
| Global Parity $\langle \hat{\mathcal{P}} \rangle$ ($p=1$) | $+1.0000$ | $+1.0000$ | $+0.8257 \pm 0.0062$ | $+0.7847 \pm 0.0068$ | Single-layer multi-qubit phase dephasing |
| Global Parity $\langle \hat{\mathcal{P}} \rangle$ ($p=2$) | $+1.0000$ | $+1.0000$ | $+0.7334 \pm 0.0075$ | $+0.6860 \pm 0.0080$ | Depth-dependent entangling error accumulation |
| QAOA Echo Fidelity $F_{\text{echo}}$ ($p=2$) | $1.0000$ | $1.0000$ | $0.7562 \pm 0.0047$ | $0.6848 \pm 0.0051$ | Cumulative two-qubit entangling echo decay |
| **Operational Metadata:** | | | | | |
| QPU Execution Runtime | $0.0\text{ s}$ | $0.12\text{ s}$ | **$13.0\text{ s}$** | **$13.0\text{ s}$** | Single-job SamplerV2 batched execution |
| Physical Qubit Sub-Chain | Ideal | Ideal | $[50, 49, 48, 47]$ | $[109, 110, 111, 98]$ | Calibration-guided greedy subgraph selection |

### Fock-Sector Decomposition & Directional Asymmetry

| Hamming Sector $w$ | Kingston Counts ($P(w)$) | Fez Counts ($P(w)$) | Physical Error Channel |
| :---: | :---: | :---: | :--- |
| $w = 0$ ($|0000\rangle$) | $77$ ($0.94\% \pm 0.11\%$) | $87$ ($1.06\% \pm 0.11\%$) | Multi-qubit thermal decay / Readout confusion |
| $w = 1$ ($|0001\rangle, \dots$) | $350$ ($4.27\% \pm 0.22\%$) | $613$ ($7.48\% \pm 0.29\%$) | Single-qubit longitudinal decay ($|1\rangle \to |0\rangle$) |
| **$w = 2$ (Target Sector)** | **$7506$ ($91.63\% \pm 0.31\%$)** | **$7241$ ($88.39\% \pm 0.35\%$)** | **Physical $N_e=2$ Fermionic Subspace** |
| $w = 3$ ($|0111\rangle, \dots$) | $211$ ($2.58\% \pm 0.18\%$) | $204$ ($2.49\% \pm 0.17\%$) | Incoherent excitation / Readout assignment bias |
| $w = 4$ ($|1111\rangle$) | $48$ ($0.59\% \pm 0.08\%$) | $47$ ($0.57\% \pm 0.08\%$) | Multi-qubit incoherent excitation |
| **Asymmetry Ratio $R_{\mathrm{asym}} = \frac{P(w=1)}{P(w=3)}$** | **$1.66 \pm 0.14$** | **$3.00 \pm 0.24$** | **Directional Relaxation & Readout Bias Indicator** |

The higher invariant retention observed on `ibm_kingston` across every observable correlates with its superior coherence times ($T_1 = 272.3\ \mu\text{s}$ vs $146.8\ \mu\text{s}$ on `ibm_fez`) and lower gate errors ($\bar{\epsilon}_{\text{CZ}} = 0.194\%$ vs $0.215\%$).

---

## 🧪 Simulation Experimentation Suite (`algoinvar_2ndexp/`)

All controlled noise-injection benchmark simulations, molecular $\mathrm{H}_2$ symmetry post-selection routines, and cross-method resource taxonomy comparisons reside inside the **`algoinvar_2ndexp/`** folder.

### 1. Controlled 4-Channel Noise Injection Sweeps ([`simulation/error_injection.py`](algoinvar_2ndexp/simulation/error_injection.py))
Evaluates the response of algorithmic invariants under parameterized Kraus operators ($50,000$ shots per point):
* **Longitudinal Relaxation ($T_1$):** Sweeping amplitude damping $\gamma \in [0.0, 0.20]$ drives the population asymmetry ratio $R_{\mathrm{asym}} = P(w=1)/P(w=3)$ monotonically from $4.27$ at $\gamma = 0.04$ to over $16.4$ at $\gamma = 0.20$. Physical hardware values ($1.66 \pm 0.14$ on Kingston vs $3.00 \pm 0.24$ on Fez) serve as a qualitative consistency check aligned with active coherence times.
* **Coherent Over-Rotation Invariance (Headline Limitation):** Sweeping angle offsets $\delta \in [-\pi/4, +\pi/4]$ on Givens rotations demonstrates that because $[g_{ij}, \hat{N}] = 0$, particle variance $\text{Var}(\hat{N}) \equiv 0.000$ and sector leakage $\mathcal{L}_{\mathrm{leak}} \equiv 0.000$ remain strictly zero across all perturbation angles. This establishes a key limitation: **exact sector preservation can coexist with degraded circuit fidelity**. Unitary retrace echo $F_{\text{echo}}$ drops quadratically as $\cos^2(\delta)$ ($1.0000 \to 0.7782$), highlighting why echo metrics are indispensable.
* **Pure Phase Dephasing Double Dissociation:** Applying phase damping Kraus operators $K_0 = \text{diag}(1, \sqrt{1-\lambda})$ and $K_1 = \text{diag}(0, \sqrt{\lambda})$ across $\lambda \in [0.0, 0.25]$ establishes a clear double dissociation:
  * In VQE, mean particle number remains tightly concentrated near the exact baseline ($\langle \hat{N} \rangle = 2.0113 \pm 0.0018$ at $\lambda = 0.25$, with residual shift $\Delta = +0.0113$ caused by gate-level inter-path phase scrambling within the compiled Givens decomposition).
  * In QAOA, phase errors anticommute with the mixer ($\{Z_k, X_k\} = 0$), causing global parity to collapse across depth $p$ ($1.0000 \to 0.1026 \pm 0.0044$ for $p=1$ and to $0.0173 \pm 0.0045$ for $p=2$).
* **Readout SPAM Confusion:** Symmetric readout noise strictly maintains $R_{\mathrm{asym}} \approx 1.00 \pm 0.04$, whereas asymmetric bias ($P(0\mid 1) = 2.5 P(1\mid 0)$) drives $R_{\mathrm{asym}} > 2.50$, proving symmetric measurement noise cannot falsely mimic directional thermal decay.

### 2. Molecular $\mathrm{H}_2$ Symmetry-Filtered Error Mitigation ([`simulation/symmetry_mitigation.py`](algoinvar_2ndexp/simulation/symmetry_mitigation.py))
Evaluates active symmetry post-selection for the electronic Hamiltonian of molecular $\mathrm{H}_2$ in the STO-3G basis ($R = 0.735\ \text{\AA}$, exact Full-CI reference energy $E_0 = -1.1372838\ \text{Ha}$, Jordan-Wigner 4-qubit mapping) under composite physical noise ($100,000$ shots per point):
* **Error Suppression:** Under severe dissipation (noise scale $s = 2.0$), unmitigated energy error surges to $\Delta E_{\text{raw}} = 520.6\ \text{mHa}$. Post-selecting onto the physical $w = 2$ sector bounds the error to $\Delta E_{\text{mit}} = 369.6\ \text{mHa}$ (a **$29.0\%$** reduction).
* **Distinction from Chemical Accuracy:** Post-selection significantly mitigates runaway dissipation, but the post-selected error remains above the conventional chemical accuracy threshold ($1.59\ \text{mHa} \approx 1.0\ \text{kcal/mol}$). Post-selection filters out unphysical states ($w \neq 2$), but does not correct in-manifold coherent rotations or dephasing within the two-particle sector.
* **Sampling Overhead:** Retained shot fractions drop from $100\%$ at $s=0$ to $32.6\%$ at $s=1.0$ and $13.5\%$ at $s=2.0$, increasing statistical uncertainty as $\sigma \propto 1/\sqrt{S_{\text{eff}}}$.

### 3. Comparative Protocol Taxonomy ([`simulation/benchmarking_comparison.py`](algoinvar_2ndexp/simulation/benchmarking_comparison.py))

| Benchmark / Verification Protocol | Workload Domain | Extra 2Q CNOT Gates | Auxiliary Ancilla Qubits | Reference Simulation Cost | Diagnostic Scope |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Clifford Randomized Benchmarking (RB)** | Random Clifford | 0 | 0 | $O(1)$ (Clifford frame) | Average gate fidelity only |
| **Cross-Entropy Benchmarking (XEB)** | Pseudo-Random | 0 | 0 | $O(2^n)$ (Exponential) | Heavy output probability |
| **Quantum Volume (QV)** | Square Model Circuits | 0 | 0 | $O(2^n)$ (Exponential) | Heavy output threshold |
| **Ancilla-Assisted Symmetry Gadgets** | Variational Ansatz | Up to $2n$ CNOTs | $1$ or more | $O(1)$ | Stabilizer syndrome projection |
| **AlgoInvar (This Work)** | **VQE & QAOA** | **0** | **0** | **$O(1)$ (Exact Theorem)** | **In situ Coherent, $T_1$, $T_2^*$, Leakage** |

---

## ⚡ AlgoInvar High-Performance C++ Core Engine

The `cpp/` directory provides a hardware-accelerated C++17 execution engine designed for high-throughput, low-latency quantum measurement analysis. It provides zero-copy bitstring parsing and CPU-intrinsic metric evaluations for high-shot-volume quantum cloud environments and utility-scale register topologies (e.g., 156-qubit IBM Heron processors).

By bypassing Python interpreter memory allocations and the Global Interpreter Lock (GIL), the C++ engine evaluates measurement distributions using single-cycle hardware population count instructions (`POPCNT` via `__builtin_popcountll` on GCC/Clang and `__popcnt64` on MSVC). This delivers up to **$115\times$ faster execution speeds** on large-scale bitstring arrays (evaluating 100,000 shots of 156-qubit registers in under $1.9\text{ ms}$) with a negligible memory footprint. Built with modern C++17 standards and cache-conscious loop unrolling, the engine features both a standalone benchmark executable and native Python bindings via `pybind11` (`algoinvar_core`), providing seamless drop-in acceleration for high-throughput quantum cloud workflows. See [`cpp/README.md`](cpp/README.md) for full architectural documentation and CMake configurations.

---

## 🚀 Execution Guide & CLI Commands

### 1. Instant Local Quickstart (Zero Cloud Credentials Required)
Clone the repository, install dependencies, and run local simulation:
```bash
git clone https://github.com/Quantum-Computing-Researcher/AlgoInvar.git
cd AlgoInvar
pip install -r requirements.txt

# Run local noiseless simulation suite for Kingston baseline
python run_ibm_kingston.py
```

### 2. Physical Quantum Hardware Execution (156-Qubit IBM Heron r2)
To run on physical hardware via IBM Quantum Runtime SamplerV2:
```bash
# Execute 40,960 physical shots on ibm_kingston (~13.0s QPU time)
python run_ibm_kingston.py --hardware --token "YOUR_IBM_QUANTUM_TOKEN"

# Execute 40,960 physical shots on ibm_fez (~13.0s QPU time)
python run_ibm_fez.py --hardware --token "YOUR_IBM_QUANTUM_TOKEN"

# Offline reverification of a previously executed IBM Quantum Job ID (0 QPU seconds)
python run_ibm_kingston.py --job-id "YOUR_FINISHED_JOB_ID" --token "YOUR_IBM_QUANTUM_TOKEN"
```

### 3. Running Controlled Simulation Experiments (`algoinvar_2ndexp/`)
Execute the complete controlled noise sweeps, molecular $\mathrm{H}_2$ error mitigation, and figure generation:
```bash
cd algoinvar_2ndexp

# Run full simulation suite (all sweeps, mitigation, and vector figures)
python run_all_experiments.py

# Optional targeted flags:
python run_all_experiments.py --noise-sweeps   # Run 4-channel noise sweeps only
python run_all_experiments.py --mitigation     # Run molecular H2 VQE post-selection only
python run_all_experiments.py --plots
```

### 4. Running the Unit Test Suite
To verify algebraic commutation relations and invariant evaluators:
```bash
python -m unittest tests/test_invariants.py
```

### 5. High-Performance C++ Core Execution
For high-shot-volume workloads and utility-scale register parsing, a native C++17 acceleration module with hardware POPCNT intrinsics is provided in `cpp/`:
```bash
cd cpp
g++ -O3 -std=c++17 src/main.cpp src/algoinvar_fast.cpp -o algoinvar_bench
./algoinvar_bench
```
See [`cpp/README.md`](cpp/README.md) for full architectural documentation, CMake instructions, and `pybind11` Python extension builds.

---

## 📜 Citation & Intellectual Property

If you find AlgoInvar useful in your research or commercial evaluation, please cite the permanent Zenodo preprint:

* **Permanent DOI:** [https://doi.org/10.5281/zenodo.23627340](https://doi.org/10.5281/zenodo.23627340)

```bibtex
@article{arqam2026algoinvar,
  title   = {AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware via Exact Algorithmic Invariants in VQE and QAOA},
  author  = {Arqam, Rehan},
  year    = {2026},
  doi     = {10.5281/zenodo.23627340},
  url     = {https://doi.org/10.5281/zenodo.23627340},
  note    = {Preprint, Zenodo CERN, Independent Researcher, Islamabad}
}
```

### Licensing Terms
* **Academic & Scientific Research:** Distributed under the [PolyForm Noncommercial License 1.0.0](LICENSE.md), granting free, royalty-free usage for educational, non-commercial scientific research.
* **Commercial Integration:** Commercial deployments, vendor cloud benchmarking services, and proprietary quantum middleware integration require a formal commercial licensing agreement. For commercial inquiries, contact:
  * **Author:** Rehan Arqam
  * **Email:** `rarqam14@gmail.com`
  * **Phone:** `+92 324 7707711`
  * **Affiliation:** Independent Researcher, Islamabad, 44000, Pakistan.
