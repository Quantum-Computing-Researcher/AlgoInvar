"""
Plotting scripts for noise response sweeps and symmetry-based error mitigation.
Generates figures for controlled error injection and molecular VQE benchmarks.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Standard clean figure styling
mpl.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 10.5,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.dpi": 300,
    "lines.linewidth": 1.6,
    "lines.markersize": 4.5,
    "mathtext.fontset": "cm",
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})

# Color palette
COLOR_NAVY = "#1F4E79"
COLOR_TEAL = "#007A78"
COLOR_GREEN = "#2D6A4F"
COLOR_RED = "#B22222"
COLOR_PURPLE = "#5E35B1"
COLOR_AMBER = "#D97706"


def plot_figure4_noise_response(
    data_dir: str = "results/error_injection",
    output_dir: str = "results/figures"
) -> None:
    """Plots the four-panel noise calibration curves with hardware reference points."""
    ad_file = os.path.join(data_dir, "amplitude_damping_sweep.json")
    coh_file = os.path.join(data_dir, "coherent_overrotation_sweep.json")
    pd_file = os.path.join(data_dir, "phase_dephasing_sweep.json")
    spam_file = os.path.join(data_dir, "spam_confusion_sweep.json")

    if not all(os.path.exists(f) for f in [ad_file, coh_file, pd_file, spam_file]):
        print("Data files not found. Run error_injection.py first.")
        return

    with open(ad_file, "r") as f:
        ad_data = json.load(f)
    with open(coh_file, "r") as f:
        coh_data = json.load(f)
    with open(pd_file, "r") as f:
        pd_data = json.load(f)
    with open(spam_file, "r") as f:
        spam_data = json.load(f)

    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.0))

    # Panel (a): Amplitude Damping
    ax_a = axes[0, 0]
    gammas = [d["gamma"] for d in ad_data]
    r_asyms = [d["R_asym"] for d in ad_data]
    p_w1 = [d["p_w1"] for d in ad_data]
    p_w3 = [d["p_w3"] for d in ad_data]

    ax_a.plot(gammas, r_asyms, color=COLOR_NAVY, marker="o", label=r"Asymmetry $R_{\mathrm{asym}} = P(w=1)/P(w=3)$")
    ax_a.plot(gammas, [p * 10 for p in p_w1], color=COLOR_RED, linestyle="--", label=r"$P(w=1) \times 10$ (loss sector)")
    ax_a.plot(gammas, [p * 10 for p in p_w3], color=COLOR_TEAL, linestyle=":", label=r"$P(w=3) \times 10$ (gain sector)")

    # Hardware reference markers
    ax_a.errorbar(0.035, 1.66, yerr=0.14, fmt="s", color=COLOR_RED, capsize=3, label=r"ibm_kingston ($1.66 \pm 0.14$)")
    ax_a.errorbar(0.075, 3.00, yerr=0.24, fmt="^", color=COLOR_PURPLE, capsize=3, label=r"ibm_fez ($3.00 \pm 0.24$)")

    ax_a.set_xlabel(r"Amplitude Damping Parameter $\gamma$")
    ax_a.set_ylabel(r"Population Asymmetry Ratio $R_{\mathrm{asym}}$")
    ax_a.set_title(r"(a) Longitudinal Relaxation ($T_1$)")
    ax_a.set_ylim(-0.2, 5.5)
    ax_a.grid(True, linestyle="--", alpha=0.5)
    ax_a.legend(loc="upper left")

    # Panel (b): Coherent Over-Rotations
    ax_b = axes[0, 1]
    deltas = [d["delta"] for d in coh_data]
    var_n = [d["var_N"] for d in coh_data]
    leakage = [d["leakage"] for d in coh_data]
    f_echo = [d["f_echo"] for d in coh_data]

    ax_b.plot(deltas, var_n, color=COLOR_GREEN, linewidth=2.0, label=r"Particle Variance $\mathrm{Var}(\hat{N}) \equiv 0$")
    ax_b.plot(deltas, leakage, color=COLOR_TEAL, linestyle="--", label=r"Out-of-Sector Population $\mathcal{L}_{\mathrm{leak}} \equiv 0$")
    ax_b.plot(deltas, f_echo, color=COLOR_AMBER, linestyle="-.", label=r"Echo Fidelity $F_{\mathrm{echo}}$")

    ax_b.set_xlabel(r"Angle Offset $\delta$ (radians)")
    ax_b.set_ylabel("Metric Value")
    ax_b.set_title(r"(b) Coherent Rotation Offset")
    ax_b.set_ylim(-0.05, 1.15)
    ax_b.grid(True, linestyle="--", alpha=0.5)
    ax_b.legend(loc="center right")

    # Panel (c): Pure Phase Dephasing
    ax_c = axes[1, 0]
    lambdas = [d["lambda"] for d in pd_data]
    vqe_var = [d["vqe_var_N"] for d in pd_data]
    qaoa_p1 = [d["qaoa_parity_p1"] for d in pd_data]
    qaoa_p2 = [d["qaoa_parity_p2"] for d in pd_data]

    ax_c.plot(lambdas, vqe_var, color=COLOR_GREEN, linewidth=2.0, label=r"VQE $\mathrm{Var}(\hat{N})$ ($[\hat{N}, Z_k]=0$)")
    ax_c.plot(lambdas, qaoa_p1, color=COLOR_NAVY, marker="s", label=r"QAOA Parity $\langle \hat{\mathcal{P}} \rangle$ ($p=1$)")
    ax_c.plot(lambdas, qaoa_p2, color=COLOR_PURPLE, marker="^", label=r"QAOA Parity $\langle \hat{\mathcal{P}} \rangle$ ($p=2$)")

    ax_c.axhline(0.8257, color=COLOR_RED, linestyle=":", alpha=0.7, label="ibm_kingston ($p=1$)")
    ax_c.axhline(0.7847, color=COLOR_PURPLE, linestyle=":", alpha=0.7, label="ibm_fez ($p=1$)")

    ax_c.set_xlabel(r"Phase Damping Parameter $\lambda$")
    ax_c.set_ylabel("Expectation Value")
    ax_c.set_title(r"(c) Pure Phase Dephasing ($T_2$)")
    ax_c.set_ylim(-0.05, 1.15)
    ax_c.grid(True, linestyle="--", alpha=0.5)
    ax_c.legend(loc="lower left")

    # Panel (d): Measurement Readout Confusion
    ax_d = axes[1, 1]
    epsilons = [d["epsilon"] for d in spam_data]
    sym_r = [d["sym_R_asym"] for d in spam_data]
    asym_r = [d["asym_R_asym"] for d in spam_data]

    ax_d.plot(epsilons, sym_r, color=COLOR_TEAL, linestyle="--", marker="s", label=r"Symmetric SPAM ($P(0|1) = P(1|0)$)")
    ax_d.plot(epsilons, asym_r, color=COLOR_RED, marker="o", label=r"Asymmetric SPAM ($P(0|1) = 2.5 P(1|0)$)")
    ax_d.axhline(1.0, color="gray", linestyle="-", alpha=0.5)

    ax_d.set_xlabel(r"Readout Error Rate $\epsilon$")
    ax_d.set_ylabel(r"Measured Asymmetry $R_{\mathrm{asym}}$")
    ax_d.set_title(r"(d) Measurement Readout Confusion")
    ax_d.set_ylim(0.5, 3.2)
    ax_d.grid(True, linestyle="--", alpha=0.5)
    ax_d.legend(loc="upper left")

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "fig4_controlled_noise_response.pdf")
    png_path = os.path.join(output_dir, "fig4_controlled_noise_response.png")
    plt.savefig(pdf_path, bbox_inches="tight")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Generated Figure 4:\n  {pdf_path}\n  {png_path}")


def plot_figure5_symmetry_mitigation(
    data_dir: str = "results/symmetry_mitigation",
    output_dir: str = "results/figures"
) -> None:
    """Plots molecular H2 ground-state energy error vs. noise level."""
    json_file = os.path.join(data_dir, "h2_vqe_mitigation_data.json")
    if not os.path.exists(json_file):
        print(f"Data file not found: {json_file}")
        return

    with open(json_file, "r") as f:
        data = json.load(f)

    noise_scales = [d["noise_scale"] for d in data]
    delta_raw = [d["delta_e_raw_mHa"] for d in data]
    delta_mit = [d["delta_e_mitigated_mHa"] for d in data]

    fig, ax = plt.subplots(figsize=(6.5, 4.2))

    ax.plot(noise_scales, delta_raw, color=COLOR_RED, marker="o", label=r"Unmitigated VQE ($\Delta E_{\mathrm{raw}}$)")
    ax.plot(noise_scales, delta_mit, color=COLOR_GREEN, marker="s", label=r"In-Sector Post-Selection ($w=2$)")

    ax.axhline(1.59, color=COLOR_NAVY, linestyle="--", label=r"Chemical Accuracy Threshold ($1.59\ \mathrm{mHa}$)")
    ax.fill_between(noise_scales, 0, 1.59, color=COLOR_NAVY, alpha=0.08)

    ax.set_xlabel("Noise Scale Factor")
    ax.set_ylabel(r"Energy Error $|E - E_{\mathrm{exact}}|$ (mHa)")
    ax.set_title(r"Molecular $\mathrm{H}_2$ Ground State ($R = 0.735\ \mathrm{\AA}$)")
    ax.set_ylim(-0.2, max(delta_raw) * 1.1)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "fig5_symmetry_error_mitigation.pdf")
    png_path = os.path.join(output_dir, "fig5_symmetry_error_mitigation.png")
    plt.savefig(pdf_path, bbox_inches="tight")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Generated Figure 5:\n  {pdf_path}\n  {png_path}")


def plot_figure6_method_comparison(
    output_dir: str = "results/figures"
) -> None:
    """Plots resource overhead comparison across methods."""
    protocols = ["Clifford RB", "XEB", "QST", "Ancilla-Assisted", "AlgoInvar"]
    ancillas = [0, 0, 0, 1, 0]
    extra_gates = [0, 0, 0, 8, 0]

    x = np.arange(len(protocols))
    width = 0.30

    fig, ax = plt.subplots(figsize=(7.0, 4.0))

    ax.bar(x - width/2, extra_gates, width, label="Additional Two-Qubit Gates", color=COLOR_RED, alpha=0.85)
    ax.bar(x + width/2, ancillas, width, label="Auxiliary Ancilla Qubits", color=COLOR_PURPLE, alpha=0.85)

    ax.set_ylabel("Resource Count")
    ax.set_title("Resource Overhead by Verification and Benchmarking Method")
    ax.set_xticks(x)
    ax.set_xticklabels(protocols)
    ax.set_ylim(0, 10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper left")

    sim_complexities = ["$O(1)$", "$O(2^n)$", "$O(4^n)$", "$O(1)$", "$O(1)$"]
    for i, txt in enumerate(sim_complexities):
        ax.text(x[i], 8.5, f"Sim: {txt}", ha="center", fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="gray", alpha=0.7))

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "fig6_method_tradeoff_comparison.pdf")
    png_path = os.path.join(output_dir, "fig6_method_tradeoff_comparison.png")
    plt.savefig(pdf_path, bbox_inches="tight")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Generated Figure 6:\n  {pdf_path}\n  {png_path}")


def run_all_plots(
    noise_dir: str = "results/error_injection",
    mitigation_dir: str = "results/symmetry_mitigation",
    output_dir: str = "results/figures"
) -> None:
    """Generates all figures from saved simulation datasets."""
    plot_figure4_noise_response(data_dir=noise_dir, output_dir=output_dir)
    plot_figure5_symmetry_mitigation(data_dir=mitigation_dir, output_dir=output_dir)
    plot_figure6_method_comparison(output_dir=output_dir)


if __name__ == "__main__":
    run_all_plots()
