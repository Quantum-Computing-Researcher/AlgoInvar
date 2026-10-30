"""
"This is the Export Engine for AlgoInvar Register-Width Scaling"
We use this module to generate multi-sheet Excel reports and publication figures
across register widths n = [4, 8, 12, 16, 32, 64].

Produces:

1. Excel Workbook (.xlsx) with Executive Summary,
VQE Invariants, QAOA Invariants,
and Hardware Metadata.

2. Figures (.png and vector .pdf) for LaTeX / RevTeX papers.
"""

import os
import sys
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXP1_DIR = os.path.join(PROJECT_ROOT, "01_algoinvar_n4_hardware_baseline")
for p in [PROJECT_ROOT, EXP1_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from algoinvar.hardware.ibm_runner import analyze_circuit_results
except ImportError:
    import importlib
    sys.modules["algoinvar"] = importlib.import_module("01_algoinvar_n4_hardware_baseline")
    from algoinvar.hardware.ibm_runner import analyze_circuit_results

# We configure Matplotlib with serif typography for publication figures

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "lines.linewidth": 1.5,
    "grid.alpha": 0.4
})


def export_scaling_to_excel(report: Dict[str, Any], filepath: str) -> str:
    """
    We export full benchmark metrics across all register widths n into a four-tab
    Excel workbook (.xlsx):
      1. Executive_Summary: Side-by-side comparison of Exact Reference, Noiseless Sim,
         IBM Hardware, and Verdict for each invariant across n = 4, 8, 12, 16, 32, 64.
      2. VQE_Invariants: Particle number expectation <N>, variance Var(N), subspace leakage,
         and retrace echo fidelity per width n.
      3. QAOA_Invariants: Global Z2 parity <P> at depths p=1, p=2 and retrace echo fidelity per width n.
      4. Hardware_Metadata: Target processor, architecture, timestamp, physical chains, Job ID,
         QPU duration, and shot count.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    widths = report.get("qubit_widths", [4, 8, 12, 16, 32, 64])
    by_width = report.get("results_by_width", {})
    backend_name = report.get("backend", "IBM Hardware")
    backend_title = backend_name.replace("_", " ").title()
    col_hw = f"IBM {backend_title} (156Q)"

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # 1. Executive Summary Sheet
        # Here we assemble the 6 core benchmark rows for each evaluated register width n

        summary_rows = []
        for n in widths:
            w_entry = by_width.get(str(n), {})
            sim = w_entry.get("simulations", {}).get("noiseless", {})
            hw = w_entry.get("hardware")
            hw_metrics = hw.get("metrics", {}) if hw else {}

            summary_rows.extend([
                {
                    "Benchmark / Metric": f"VQE Particle Expectation <N> (n={n})",
                    "Target State": f"N_e = 2 fermions (n={n})",
                    "Exact Reference": 2.0000,
                    "Noiseless Sim": sim.get("vqe_particle_l2", {}).get("mean_N", np.nan),
                    col_hw: hw_metrics.get("vqe_particle_l2", {}).get("mean_N", np.nan),
                    "Verdict": "PASSED" if hw_metrics.get("vqe_particle_l2", {}).get("passed") else ("SIM ONLY" if not hw else "FAILED")
                },
                {
                    "Benchmark / Metric": f"VQE Particle Variance Var(N) (n={n})",
                    "Target State": f"N_e = 2 fermions (n={n})",
                    "Exact Reference": 0.0000,
                    "Noiseless Sim": sim.get("vqe_particle_l2", {}).get("var_N", np.nan),
                    col_hw: hw_metrics.get("vqe_particle_l2", {}).get("var_N", np.nan),
                    "Verdict": "PASSED" if hw_metrics.get("vqe_particle_l2", {}).get("passed") else ("SIM ONLY" if not hw else "FAILED")
                },
                {
                    "Benchmark / Metric": f"VQE Retrace Echo Fidelity (n={n})",
                    "Target State": f"U^dagger U = I (n={n})",
                    "Exact Reference": 1.0000,
                    "Noiseless Sim": sim.get("vqe_retrace", {}).get("return_fidelity", np.nan),
                    col_hw: hw_metrics.get("vqe_retrace", {}).get("return_fidelity", np.nan),
                    "Verdict": "PASSED" if hw_metrics.get("vqe_retrace", {}).get("passed") else ("SIM ONLY" if not hw else "FAILED")
                },
                {
                    "Benchmark / Metric": f"QAOA Z2 Parity (p=1) (n={n})",
                    "Target State": f"Max-Cut Ring Graph (n={n})",
                    "Exact Reference": 1.0000,
                    "Noiseless Sim": sim.get("qaoa_parity_p1", {}).get("global_parity", np.nan),
                    col_hw: hw_metrics.get("qaoa_parity_p1", {}).get("global_parity", np.nan),
                    "Verdict": "PASSED" if hw_metrics.get("qaoa_parity_p1", {}).get("passed") else ("SIM ONLY" if not hw else "FAILED")
                },
                {
                    "Benchmark / Metric": f"QAOA Z2 Parity (p=2) (n={n})",
                    "Target State": f"Max-Cut Ring Graph (n={n})",
                    "Exact Reference": 1.0000,
                    "Noiseless Sim": sim.get("qaoa_parity_p2", {}).get("global_parity", np.nan),
                    col_hw: hw_metrics.get("qaoa_parity_p2", {}).get("global_parity", np.nan),
                    "Verdict": "PASSED" if hw_metrics.get("qaoa_parity_p2", {}).get("passed") else ("SIM ONLY" if not hw else "FAILED")
                },
                {
                    "Benchmark / Metric": f"QAOA Retrace Echo Fidelity (p=2) (n={n})",
                    "Target State": f"U^dagger U = I (n={n})",
                    "Exact Reference": 1.0000,
                    "Noiseless Sim": sim.get("qaoa_retrace_p2", {}).get("retrace_fidelity", np.nan),
                    col_hw: hw_metrics.get("qaoa_retrace_p2", {}).get("retrace_fidelity", np.nan),
                    "Verdict": "PASSED" if hw_metrics.get("qaoa_retrace_p2", {}).get("passed") else ("SIM ONLY" if not hw else "FAILED")
                }
            ])

        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Executive_Summary", index=False)

        # 2. VQE Invariants Sheet
        # We record <N>, Var(N), Fock subspace leakage, and retrace echo fidelity per width n

        vqe_rows = []
        for n in widths:
            w_entry = by_width.get(str(n), {})
            sim = w_entry.get("simulations", {}).get("noiseless", {})
            hw = w_entry.get("hardware")
            hw_metrics = hw.get("metrics", {}) if hw else {}

            for src_name, metrics in [(f"Noiseless_Simulation (n={n})", sim), (f"{backend_title}_Hardware (n={n})", hw_metrics)]:
                if metrics:
                    c1 = metrics.get("vqe_particle_l2", {})
                    c2 = metrics.get("vqe_retrace", {})
                    vqe_rows.append({
                        "Platform": src_name,
                        "Mean Particle <N>": c1.get("mean_N", np.nan),
                        "Variance Var(N)": c1.get("var_N", np.nan),
                        "Fock Subspace Leakage": c1.get("leakage", np.nan),
                        "Retrace Echo Fidelity": c2.get("return_fidelity", np.nan),
                        "Total Shots": c1.get("shots", np.nan)
                    })
        pd.DataFrame(vqe_rows).to_excel(writer, sheet_name="VQE_Invariants", index=False)

        # 3. QAOA Invariants Sheet
        # We record global Z2 parity <P> at p=1, p=2 and retrace echo fidelity per width n

        qaoa_rows = []
        for n in widths:
            w_entry = by_width.get(str(n), {})
            sim = w_entry.get("simulations", {}).get("noiseless", {})
            hw = w_entry.get("hardware")
            hw_metrics = hw.get("metrics", {}) if hw else {}

            for src_name, metrics in [(f"Noiseless_Simulation (n={n})", sim), (f"{backend_title}_Hardware (n={n})", hw_metrics)]:
                if metrics:
                    p1 = metrics.get("qaoa_parity_p1", {})
                    p2 = metrics.get("qaoa_parity_p2", {})
                    ret = metrics.get("qaoa_retrace_p2", {})
                    qaoa_rows.append({
                        "Platform": src_name,
                        "Global Parity <P> (p=1)": p1.get("global_parity", np.nan),
                        "Global Parity <P> (p=2)": p2.get("global_parity", np.nan),
                        "Retrace Echo Fidelity (p=2)": ret.get("retrace_fidelity", np.nan),
                        "Total Shots": p1.get("shots", np.nan)
                    })
        pd.DataFrame(qaoa_rows).to_excel(writer, sheet_name="QAOA_Invariants", index=False)

        # 4. Hardware Metadata Sheet
        # We store processor identity, evaluated register widths, physical chains, Job ID, and QPU time

        any_hw = next((by_width.get(str(n), {}).get("hardware") for n in widths if by_width.get(str(n), {}).get("hardware")), None)
        chains_used = {f"n={n}": by_width.get(str(n), {}).get("hardware", {}).get("chain") for n in widths} if any_hw else "N/A"
        hw_meta = [
            {"Property": "Target Processor", "Value": report.get("backend", "IBM Hardware")},
            {"Property": "Architecture", "Value": "156-qubit IBM Heron processor"},
            {"Property": "Timestamp", "Value": report.get("timestamp", "")},
            {"Property": "Register Widths Evaluated", "Value": str(widths)},
            {"Property": "Physical Qubits Used", "Value": str(chains_used) if any_hw else "N/A"},
            {"Property": "IBM Job ID", "Value": any_hw.get("job_id", "N/A") if any_hw else "N/A"},
            {"Property": "Reported QPU Duration (seconds)", "Value": any_hw.get("qpu_seconds", 0.0) if any_hw else 0.0},
            {"Property": "Shots per Circuit Setting", "Value": report.get("shots_per_circuit", 8192)}
        ]
        pd.DataFrame(hw_meta).to_excel(writer, sheet_name="Hardware_Metadata", index=False)

    return filepath


def export_scaling_publication_figures(report: Dict[str, Any], output_dir: str = "figures") -> List[str]:
    """
    We generate two-panel scaling figures (.png and .pdf) comparing theoretical invariants,
    noiseless simulation, and IBM hardware across n = [4, 8, 12, 16, 32, 64].
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    widths = report.get("qubit_widths", [4, 8, 12, 16, 32, 64])
    by_width = report.get("results_by_width", {})
    backend_name = report.get("backend", "IBM Hardware")
    backend_title = backend_name.replace("_", " ").title()
    hw_prefix = backend_name.lower()
    has_hw = any(by_width.get(str(n), {}).get("hardware") for n in widths)

    # Figure 1: Invariant Preservation Across Register Widths (VQE & QAOA)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5), dpi=300)

    # Panel (a): VQE In-Sector Preservation (1 - Leakage) and VQE Echo vs Register Width n
    ax1 = axes[0]
    exact_line = [1.0 for _ in widths]
    sim_in_sector = [
        1.0 - by_width.get(str(n), {}).get("simulations", {}).get("noiseless", {}).get("vqe_particle_l2", {}).get("leakage", 0.0)
        for n in widths
    ]
    ax1.plot(widths, exact_line, "--", color="#2ca02c", lw=1.8, label="Exact Theory (Invariant = 1.0)")
    ax1.plot(widths, sim_in_sector, "o-", color="#1f77b4", lw=1.8, ms=6, label="Noiseless Simulator (Aer)")

    if has_hw:
        hw_in_sector = [
            1.0 - (by_width.get(str(n), {}).get("hardware") or {}).get("metrics", {}).get("vqe_particle_l2", {}).get("leakage", np.nan)
            for n in widths
        ]
        hw_vqe_echo = [
            (by_width.get(str(n), {}).get("hardware") or {}).get("metrics", {}).get("vqe_retrace", {}).get("return_fidelity", np.nan)
            for n in widths
        ]
        ax1.plot(widths, hw_in_sector, "s-", color="#d62728", lw=2.0, ms=6, label=f"IBM {backend_title} In-Sector (1-Leak)")
        ax1.plot(widths, hw_vqe_echo, "^--", color="#ff7f0e", lw=1.8, ms=6, label=f"IBM {backend_title} VQE Echo (F)")

    ax1.set_xlabel("Register Width n (Qubits)")
    ax1.set_ylabel("Normalized Invariant Metric")
    ax1.set_title(f"VQE Invariant Scaling ({backend_title})", fontweight="bold")
    ax1.set_xticks(widths)
    ax1.set_ylim(0.0, 1.15)
    ax1.legend(loc="lower left", framealpha=0.9)
    ax1.grid(axis="both", linestyle=":", alpha=0.6)

    # Panel (b): QAOA Global Z2 Parity (p=1, p=2) and Echo Fidelity vs Register Width n
    ax2 = axes[1]
    sim_qaoa_p1 = [
        by_width.get(str(n), {}).get("simulations", {}).get("noiseless", {}).get("qaoa_parity_p1", {}).get("global_parity", 1.0)
        for n in widths
    ]
    ax2.plot(widths, exact_line, "--", color="#2ca02c", lw=1.8, label="Exact Theory (Invariant = 1.0)")
    ax2.plot(widths, sim_qaoa_p1, "o-", color="#1f77b4", lw=1.8, ms=6, label="Noiseless Simulator (Aer)")

    if has_hw:
        hw_qp1 = [
            (by_width.get(str(n), {}).get("hardware") or {}).get("metrics", {}).get("qaoa_parity_p1", {}).get("global_parity", np.nan)
            for n in widths
        ]
        hw_qp2 = [
            (by_width.get(str(n), {}).get("hardware") or {}).get("metrics", {}).get("qaoa_parity_p2", {}).get("global_parity", np.nan)
            for n in widths
        ]
        hw_qe2 = [
            (by_width.get(str(n), {}).get("hardware") or {}).get("metrics", {}).get("qaoa_retrace_p2", {}).get("retrace_fidelity", np.nan)
            for n in widths
        ]
        ax2.plot(widths, hw_qp1, "s-", color="#d62728", lw=2.0, ms=6, label=f"IBM {backend_title} Parity (p=1)")
        ax2.plot(widths, hw_qp2, "D--", color="#9467bd", lw=1.8, ms=6, label=f"IBM {backend_title} Parity (p=2)")
        ax2.plot(widths, hw_qe2, "^:", color="#ff7f0e", lw=1.8, ms=6, label=f"IBM {backend_title} QAOA Echo (p=2)")

    ax2.set_xlabel("Register Width n (Qubits)")
    ax2.set_ylabel("Normalized Invariant Metric")
    ax2.set_title(f"QAOA Parity Scaling ({backend_title})", fontweight="bold")
    ax2.set_xticks(widths)
    ax2.set_ylim(-0.1, 1.15)
    ax2.legend(loc="lower left", framealpha=0.9)
    ax2.grid(axis="both", linestyle=":", alpha=0.6)

    mode = report.get("mode", "simulation")
    mode_tag = {"simulation": "sim", "hardware_run": "hw", "reverification": "verification"}.get(mode, mode)
    plt.tight_layout()
    f1_png = os.path.join(output_dir, f"{hw_prefix}_scaling_{mode_tag}_fig1_invariants.png")
    f1_pdf = os.path.join(output_dir, f"{hw_prefix}_scaling_{mode_tag}_fig1_invariants.pdf")
    plt.savefig(f1_png, dpi=300)
    plt.savefig(f1_pdf)
    plt.close()
    generated_files.extend([f1_png, f1_pdf])

    return generated_files
