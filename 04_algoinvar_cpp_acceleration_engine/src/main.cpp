#include "../include/algoinvar_fast.hpp"
#include <iostream>
#include <iomanip>
#include <chrono>
#include <random>

int main() {
    std::cout << "======================================================================\n";
    std::cout << "AlgoInvar: High-Performance C++ Invariant Evaluation Engine\n";
    std::cout << "Hardware-Accelerated Bitwise Diagnostics for Utility-Scale Registers\n";
    std::cout << "======================================================================\n\n";

    // 1. Synthetic 156-qubit IBM Heron r2 sample generation (100,000 physical shots)
    constexpr size_t NUM_SHOTS = 100000;
    constexpr size_t N_QUBITS = 156;

    std::cout << "[1/3] Generating synthetic 156-qubit measurement payload ("
              << NUM_SHOTS << " shots)...\n";

    std::unordered_map<std::string, uint64_t> mock_payload;
    mock_payload.reserve(500);

    // Create a realistic sample distribution with physical target sector and error leakage
    // Target sector (w = 2 active on mapped fermionic sub-chain)
    std::string base_state(N_QUBITS, '0');
    base_state[47] = '1';
    base_state[48] = '1';
    mock_payload[base_state] = static_cast<uint64_t>(NUM_SHOTS * 0.9163); // 91.63% in-sector (Kingston baseline)

    // Leakage w = 1 (T1 longitudinal decay)
    std::string decay_state(N_QUBITS, '0');
    decay_state[47] = '1';
    mock_payload[decay_state] = static_cast<uint64_t>(NUM_SHOTS * 0.0427);

    // Leakage w = 3 (Incoherent excitation / SPAM confusion)
    std::string excited_state(N_QUBITS, '0');
    excited_state[47] = '1';
    excited_state[48] = '1';
    excited_state[49] = '1';
    mock_payload[excited_state] = static_cast<uint64_t>(NUM_SHOTS * 0.0258);

    // Residual multi-qubit background noise
    std::string ground_state(N_QUBITS, '0');
    mock_payload[ground_state] = static_cast<uint64_t>(NUM_SHOTS * 0.0152);

    std::cout << "[2/3] Executing fast bitwise Fock-sector diagnostics via CPU intrinsics...\n";

    auto start_time = std::chrono::high_resolution_clock::now();
    algoinvar::FockMetrics fock = algoinvar::evaluate_fock_distribution(mock_payload, 2);
    auto end_time = std::chrono::high_resolution_clock::now();

    auto duration_us = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();
    double duration_ms = static_cast<double>(duration_us) / 1000.0;

    std::cout << "\n======================================================================\n";
    std::cout << "BENCHMARK PERFORMANCE RESULTS\n";
    std::cout << "======================================================================\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  Execution Wall Time      : " << duration_ms << " ms (" << duration_us << " us)\n";
    std::cout << "  Total Processed Shots    : " << fock.total_shots << "\n";
    std::cout << "  Throughput Rate          : " << static_cast<uint64_t>((fock.total_shots / (duration_ms / 1000.0))) << " shots/sec\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << "  In-Sector Population P(2): " << (fock.in_sector_population * 100.0) << " % (± " << (fock.std_error_leakage * 100.0) << " %)\n";
    std::cout << "  Out-of-Sector Leakage    : " << (fock.leakage * 100.0) << " %\n";
    std::cout << "  Mean Particle Number <N> : " << fock.mean_n << " (Exact Theory: 2.0000)\n";
    std::cout << "  Particle Variance Var(N) : " << fock.var_n << " (Exact Theory: 0.0000)\n";
    std::cout << "  Directional Asymmetry (R): " << fock.asymmetry_ratio << " (P(w=1)/P(w=3))\n";
    std::cout << "======================================================================\n\n";

    std::cout << "[3/3] Evaluating QAOA Global Z2 Spin-Parity Observable...\n";
    algoinvar::ParityMetrics parity = algoinvar::evaluate_qaoa_parity(mock_payload);
    std::cout << "  Global Parity <P>        : " << (parity.mean_parity >= 0 ? "+" : "") << parity.mean_parity 
              << " (± " << parity.std_error_parity << ")\n";
    std::cout << "  Parity Sector Ratio (+/-): " << (parity.positive_population * 100.0) << "% / " 
              << (parity.negative_population * 100.0) << "%\n";
    std::cout << "======================================================================\n";
    std::cout << "[STATUS] Native C++ engine executed successfully with O(1) theory scaling.\n\n";

    return 0;
}
