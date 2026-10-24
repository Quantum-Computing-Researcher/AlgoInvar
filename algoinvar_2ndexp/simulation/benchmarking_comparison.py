"""
Comparison of symmetry verification methods and hardware benchmarking protocols.
"""

from typing import Dict, List, Any
import os
import json
import pandas as pd


def get_benchmarking_comparison_data() -> List[Dict[str, Any]]:
    """Returns benchmarking comparison metrics across standard protocols."""
    return [
        {
            "Protocol": "Clifford RB",
            "Target Workload": "Synthetic Random Clifford",
            "Auxiliary Ancillas": 0,
            "Extra Entangling Gates": 0,
            "Circuit Depth Overhead": "1.0x",
            "Classical Simulation Cost": "O(1)",
            "Scalability Horizon": "Moderate (~100 Qubits)",
            "Diagnosed Noise Physics": "Average gate infidelity (EPC)",
            "Active Mitigation": "No",
            "Algorithmic Workload Fidelity": "Low"
        },
        {
            "Protocol": "Cross-Entropy Benchmarking (XEB)",
            "Target Workload": "Synthetic Pseudo-Random",
            "Auxiliary Ancillas": 0,
            "Extra Entangling Gates": 0,
            "Circuit Depth Overhead": "1.0x",
            "Classical Simulation Cost": "O(2^n)",
            "Scalability Horizon": "Limited by simulation (n <= 50)",
            "Diagnosed Noise Physics": "Heavy output probability fidelity",
            "Active Mitigation": "No",
            "Algorithmic Workload Fidelity": "Low"
        },
        {
            "Protocol": "Quantum State Tomography (QST)",
            "Target Workload": "Arbitrary State",
            "Auxiliary Ancillas": 0,
            "Extra Entangling Gates": 0,
            "Circuit Depth Overhead": "1.0x",
            "Classical Simulation Cost": "O(4^n)",
            "Scalability Horizon": "Limited by tomography (n <= 8)",
            "Diagnosed Noise Physics": "Full density matrix",
            "Active Mitigation": "No",
            "Algorithmic Workload Fidelity": "Complete"
        },
        {
            "Protocol": "Ancilla-Assisted Symmetry Verification",
            "Target Workload": "VQE Chemistry",
            "Auxiliary Ancillas": 1,
            "Extra Entangling Gates": "2n CNOTs",
            "Circuit Depth Overhead": "1.6x - 2.5x",
            "Classical Simulation Cost": "O(1)",
            "Scalability Horizon": "Constrained by routing & cross-talk",
            "Diagnosed Noise Physics": "Parity violation flag",
            "Active Mitigation": "Yes",
            "Algorithmic Workload Fidelity": "Moderate"
        },
        {
            "Protocol": "AlgoInvar",
            "Target Workload": "VQE & QAOA",
            "Auxiliary Ancillas": 0,
            "Extra Entangling Gates": 0,
            "Circuit Depth Overhead": "1.0x",
            "Classical Simulation Cost": "O(1)",
            "Scalability Horizon": "Arbitrary width n (Analytical reference)",
            "Diagnosed Noise Physics": "Coherent drift, relaxation asymmetry, dephasing, SPAM",
            "Active Mitigation": "Yes",
            "Algorithmic Workload Fidelity": "Exact"
        }
    ]


def generate_latex_comparison_table(data: List[Dict[str, Any]]) -> str:
    """Generates REVTeX 4-2 table comparing verification and benchmarking protocols."""
    latex = []
    latex.append(r"\begin{table*}[t]")
    latex.append(r"\caption{\label{tab:method_comparison}\textbf{Comparative Methodology and Quantitative Benchmarking Taxonomy.} Architectural and resource-overhead comparison between AlgoInvar, ancilla-assisted symmetry verification, and standard hardware benchmarking protocols.}")
    latex.append(r"\resizebox{\textwidth}{!}{%")
    latex.append(r"\begin{ruledtabular}")
    latex.append(r"\begin{tabular}{p{3.5cm} c c c c p{4.2cm} c}")
    latex.append(r"\textbf{Protocol} & \textbf{Ancillas} & \textbf{Extra 2Q Gates} & \textbf{Depth Factor} & \textbf{Classical Cost} & \textbf{Diagnosed Error Types} & \textbf{Mitigation} \\")
    latex.append(r"\hline")
    
    for row in data:
        name = row["Protocol"]
        anc = str(row["Auxiliary Ancillas"])
        gates = str(row["Extra Entangling Gates"])
        depth = str(row["Circuit Depth Overhead"])
        sim = str(row["Classical Simulation Cost"])
        diag = str(row["Diagnosed Noise Physics"])
        mit = str(row["Active Mitigation"])
        
        if "AlgoInvar" in name:
            latex.append(rf"\textbf{{{name}}} & \bm{{{anc}}} & \bm{{{gates}}} & \bm{{{depth}}} & \bm{{{sim}}} & \textbf{{{diag}}} & \bm{{{mit}}} \\")
        else:
            latex.append(rf"{name} & {anc} & {gates} & {depth} & {sim} & {diag} & {mit} \\")
            
    latex.append(r"\end{tabular}")
    latex.append(r"\end{ruledtabular}%")
    latex.append(r"}")
    latex.append(r"\end{table*}")
    
    return "\n".join(latex)


def run_benchmarking_comparison(
    output_dir: str = "results/device_calibration"
) -> Dict[str, Any]:
    """Saves comparison metrics in JSON, Excel, and LaTeX formats."""
    os.makedirs(output_dir, exist_ok=True)
    data = get_benchmarking_comparison_data()
    
    json_path = os.path.join(output_dir, "benchmarking_comparison.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
        
    excel_path = os.path.join(output_dir, "methodology_comparison.xlsx")
    pd.DataFrame(data).to_excel(excel_path, sheet_name="Comparison_Taxonomy", index=False)
    
    latex_code = generate_latex_comparison_table(data)
    latex_path = os.path.join(output_dir, "table_method_comparison.tex")
    with open(latex_path, "w") as f:
        f.write(latex_code)
        
    return {"data": data, "latex": latex_code}


if __name__ == "__main__":
    run_benchmarking_comparison()
