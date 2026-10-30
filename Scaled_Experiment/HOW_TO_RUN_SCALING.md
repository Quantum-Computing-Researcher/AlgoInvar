# AlgoInvar Multi-Width Register Scaling Suite ($n = 4, 8, 12, 16, 32, 64$)

This directory (`Scaled_Experiment/`) contains the self-contained execution drivers, circuit generators, calibration-guided subgraph routers, and verified experimental datasets for evaluating the **AlgoInvar** 5-circuit benchmark protocol across six register widths $n \in \{4, 8, 12, 16, 32, 64\}$—crossing the **50-qubit classical statevector simulation threshold**—on two independent 156-qubit IBM Heron r2 processors (`ibm_kingston` and `ibm_fez`).

---

## 1. Benchmark Protocol & Batched Single-Job Architecture

For each register width $n \in \{4, 8, 12, 16, 32, 64\}$, all five benchmark circuits are constructed afresh and batched into a **single `SamplerV2` hardware payload** ($6 \text{ widths} \times 5 \text{ circuits} = 30 \text{ ISA circuits}$ per processor at $8,192$ shots per circuit $= 245,760$ physical shots per processor):

1. `vqe_particle_l2`: Excitation-conserving Givens network ($N_e = 2$ fermions initialized on $|\psi_0\rangle = |110^{\otimes(n-2)}\rangle$, $L = 2$ layers, `seed=42`, $Z$-basis readout).
2. `vqe_retrace`: VQE unitary retrace echo $U^\dagger(\vec{\theta}) U(\vec{\theta}) = I$ ($N_e = 2$, $L = 2$, $Z$-basis readout).
3. `qaoa_parity_p1`: QAOA Max-Cut on an $n$-vertex 1D ring graph ($p = 1$, $\gamma_1 = 0.39, \beta_1 = 0.25$, terminal $H^{\otimes n}$ for $X$-basis readout).
4. `qaoa_parity_p2`: QAOA Max-Cut on an $n$-vertex 1D ring graph ($p = 2$, $\gamma_2 = 0.78, \beta_2 = 0.50$, $X$-basis readout).
5. `qaoa_retrace_p2`: QAOA unitary retrace echo $U^\dagger_{\text{QAOA}} U_{\text{QAOA}} = I$ ($p = 2$, $X$-basis readout).

* **Zero Classical Simulation at Large $n$:** For widths $n \le 16$, a local noiseless `AerSimulator` verification baseline is executed alongside the analytical reference. For widths $n \in \{32, 64\}$ (where dense $2^{64}$ statevector simulation requires $295\text{ EiB}$ of RAM), classical statevector simulation is bypassed in favor of the exact $O(1)$ analytical conservation theorems ($\langle \hat{N} \rangle \equiv 2.0000$, $\text{Var}(\hat{N}) \equiv 0.0000$, $P(w=2) \equiv 1.0000$, $\langle \hat{\mathcal{P}} \rangle \equiv +1.0000$, $F_{\text{echo}} \equiv 1.0000$) and linear $O(S \cdot n)$ bitstring post-processing (accelerated via 64-bit hardware `POPCNT` intrinsics in [`../cpp/`](../cpp/README.md)).

---

## 2. Verified IBM Heron r2 Hardware Executions (Campaign 2)

| Processor | Architecture | IBM Quantum Job ID | Total Shots | QPU Time | Queue & Calibration Regime |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`ibm_kingston`** | 156Q Heron r2 | `dbhkepune4hc73bd3bg0` | $245,760$ ($30 \times 8,192$) | `69.0 s` | High-contention queue ($\sim 140$ pending jobs, $4$–$5$ interim calibration updates) |
| **`ibm_fez`** | 156Q Heron r2 | `dbhm1hmne4hc73bd64f0` | $245,760$ ($30 \times 8,192$) | `68.0 s` | Quasi-synchronous low queue ($\sim 6$ pending jobs after fresh calibration update) |

### Key Empirical Results Across $n = 4 \to 64$
* **Peak Low-Queue Sector Confinement ($n = 4$, `ibm_fez`):** $\langle \hat{N} \rangle = 1.9799 \pm 0.0036$, $\text{Var}(\hat{N}) = 0.1045$, **$P(w=2) = 92.04\% \pm 0.30\%$**, $F_{\text{echo}} = 82.76\% \pm 0.42\%$, and QAOA parity $\langle \hat{\mathcal{P}} \rangle_{p=1} = +0.8271 \pm 0.0062$.
* **64-Qubit Utility-Scale Verification ($n = 64$, Crossing the 50Q Classical Simulation Wall):**
  * **Raw Full-Register Invariants:** `ibm_kingston` preserves **$24.79\% \pm 0.48\%$** ($2,031 / 8,192$ shots) in the exact $w = 2$ sector with $F_{\text{echo}} = 9.91\% \pm 0.33\%$ ($812 / 8,192$ shots).
  * **In Situ Spectator-Deconvolved Invariants:** Deconvolving the $(n - 4) = 60$ ground-state spectator modes directly from the 64-qubit bitstrings restores **$P_{\text{act}}(w=2) = 87.29\% \pm 0.37\%$** ($F_{\text{echo}}^{\text{act}} = 78.78\% \pm 0.45\%$, $\hat{\varepsilon}_{0\to 1} = 3.25\%/\text{qubit}$) on `ibm_kingston` and **$P_{\text{act}}(w=2) = 82.85\% \pm 0.42\%$** ($F_{\text{echo}}^{\text{act}} = 70.95\% \pm 0.50\%$, $\hat{\varepsilon}_{0\to 1} = 6.91\%/\text{qubit}$) on `ibm_fez`.

---

## 3. Directory Contents & Generated Artifacts

```text
Scaled_Experiment/
├── HOW_TO_RUN_SCALING.md            # This guide
├── qubit_chain_scaling.py           # Calibration-guided greedy DFS chain selector for n = 4..64
├── scaling_circuits.py              # Parametric VQE & QAOA circuit builders for arbitrary width n
├── scaling_metrics.py               # 4-tab Excel workbook & vector PDF/PNG figure exporter
├── scaling_runner.py                # Unified execution engine (Simulation, Hardware, Reverification)
├── run_scaling_kingston.py          # CLI entry point for 156Q ibm_kingston
├── run_scaling_fez.py               # CLI entry point for 156Q ibm_fez
├── results_scaling_kingston/        # Verified outputs for ibm_kingston (Job: dbhkepune4hc73bd3bg0)
│   ├── simulation/                  # Noiseless baseline JSON, 4-tab XLSX, and figures/
│   ├── hardware_run/                # Live QPU execution JSON, 4-tab XLSX, and figures/
│   └── reverification/              # Offline reverified JSON, 4-tab XLSX, and figures/
└── results_scaling_fez/             # Verified outputs for ibm_fez (Job: dbhm1hmne4hc73bd64f0)
    ├── simulation/                  # Noiseless baseline JSON, 4-tab XLSX, and figures/
    ├── hardware_run/                # Live QPU execution JSON, 4-tab XLSX, and figures/
    └── reverification/              # Offline reverified JSON, 4-tab XLSX, and figures/
```

---

## 4. Execution Commands (Run from Repository Root)

### Mode 1: Local Simulation Mode (`0` QPU Seconds)
```powershell
python Scaled_Experiment/run_scaling_kingston.py
python Scaled_Experiment/run_scaling_fez.py
```

### Mode 2: Live IBM Hardware Execution (`SamplerV2`, `~68–69 s` QPU Time)
```powershell
python Scaled_Experiment/run_scaling_kingston.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python Scaled_Experiment/run_scaling_fez.py --hardware --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
```

### Mode 3: Offline Job Reverification (`0` QPU Seconds)
Re-fetches and audits the completed hardware jobs directly from IBM Quantum Cloud:
```powershell
python Scaled_Experiment/run_scaling_kingston.py --job-id "dbhkepune4hc73bd3bg0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
python Scaled_Experiment/run_scaling_fez.py --job-id "dbhm1hmne4hc73bd64f0" --token "YOUR_IBM_TOKEN" --crn "YOUR_IBM_CRN"
```
