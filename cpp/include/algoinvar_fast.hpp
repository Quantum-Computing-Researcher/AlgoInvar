#ifndef ALGOINVAR_FAST_HPP
#define ALGOINVAR_FAST_HPP

#include <cstdint>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <numeric>
#include <cmath>
#include <stdexcept>

#if defined(_MSC_VER)
#include <intrin.h>
#endif

namespace algoinvar {

/**
 * @brief Core metrics container for VQE fermionic particle-number conservation.
 * Evaluates in situ expectation, variance, sector retention, and physical leakage.
 */
struct FockMetrics {
    double mean_n = 0.0;
    double var_n = 0.0;
    double std_error_mean = 0.0;
    double in_sector_population = 0.0;
    double leakage = 0.0;
    double std_error_leakage = 0.0;
    double asymmetry_ratio = 0.0; // P(w=1) / P(w=3) directional relaxation diagnostic
    uint64_t total_shots = 0;
    std::unordered_map<uint32_t, uint64_t> sector_counts;
};

/**
 * @brief Core metrics container for QAOA global Z2 spin-parity conservation.
 * Tracks collective transversal X-spin parity retention across layers.
 */
struct ParityMetrics {
    double mean_parity = 0.0;
    double std_error_parity = 0.0;
    double positive_population = 0.0;
    double negative_population = 0.0;
    uint64_t total_shots = 0;
};

/**
 * @brief Cross-platform hardware-accelerated population count (Hamming weight).
 * Directly invokes native CPU POPCNT instructions in a single clock cycle.
 */
inline uint32_t hardware_popcount64(uint64_t val) noexcept {
#if defined(_MSC_VER)
    return static_cast<uint32_t>(__popcnt64(val));
#elif defined(__GNUC__) || defined(__clang__)
    return static_cast<uint32_t>(__builtin_popcountll(val));
#else
    // Portable 64-bit Hamming weight fallback
    val = val - ((val >> 1) & 0x5555555555555555ULL);
    val = (val & 0x3333333333333333ULL) + ((val >> 2) & 0x3333333333333333ULL);
    return static_cast<uint32_t>((((val + (val >> 4)) & 0x0F0F0F0F0F0F0F0FULL) * 0x0101010101010101ULL) >> 56);
#endif
}

/**
 * @brief Fast bitstring parser for measurement bitstrings (e.g., "0101" or utility-scale 156Q bitstrings).
 * Processes characters in 64-bit chunks for maximum cache efficiency.
 */
uint32_t fast_hamming_weight(std::string_view bitstring) noexcept;

/**
 * @brief Evaluates VQE particle-number sector conservation on sampled frequency counts.
 * 
 * @param counts Map of measurement bitstrings to their shot counts.
 * @param target_particles The physical theoretical electron/particle count N_e (default = 2).
 * @return FockMetrics Calculated in situ expectation, variance, leakage, and directional asymmetry.
 */
FockMetrics evaluate_fock_distribution(
    const std::unordered_map<std::string, uint64_t>& counts,
    uint32_t target_particles = 2
);

/**
 * @brief Evaluates QAOA global Z2 spin parity <P> = <X^(x) n> on transversal X-basis counts.
 * 
 * @param counts Map of measurement bitstrings to counts (measured in X-basis).
 * @return ParityMetrics Global parity expectation value and shot uncertainty.
 */
ParityMetrics evaluate_qaoa_parity(
    const std::unordered_map<std::string, uint64_t>& counts
);

} // namespace algoinvar

#endif // ALGOINVAR_FAST_HPP
