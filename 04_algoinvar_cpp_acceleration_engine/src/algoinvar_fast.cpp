#include "../include/algoinvar_fast.hpp"
#include <algorithm>
#include <cmath>

namespace algoinvar {

uint32_t fast_hamming_weight(std::string_view bitstring) noexcept {
    uint32_t weight = 0;
    const size_t len = bitstring.length();
    size_t i = 0;

    // Fast unrolled path: 8 characters per iteration
    while (i + 8 <= len) {
        weight += (bitstring[i] == '1');
        weight += (bitstring[i + 1] == '1');
        weight += (bitstring[i + 2] == '1');
        weight += (bitstring[i + 3] == '1');
        weight += (bitstring[i + 4] == '1');
        weight += (bitstring[i + 5] == '1');
        weight += (bitstring[i + 6] == '1');
        weight += (bitstring[i + 7] == '1');
        i += 8;
    }

    // Remaining tail characters
    while (i < len) {
        weight += (bitstring[i] == '1');
        ++i;
    }

    return weight;
}

FockMetrics evaluate_fock_distribution(
    const std::unordered_map<std::string, uint64_t>& counts,
    uint32_t target_particles
) {
    FockMetrics metrics;
    if (counts.empty()) {
        return metrics;
    }

    uint64_t total_shots = 0;
    double sum_n = 0.0;
    double sum_n2 = 0.0;

    for (const auto& [bitstring, count] : counts) {
        total_shots += count;
        uint32_t w = fast_hamming_weight(bitstring);
        metrics.sector_counts[w] += count;

        double d_w = static_cast<double>(w);
        double d_count = static_cast<double>(count);
        sum_n += d_w * d_count;
        sum_n2 += (d_w * d_w) * d_count;
    }

    if (total_shots == 0) {
        return metrics;
    }

    metrics.total_shots = total_shots;
    const double d_total = static_cast<double>(total_shots);

    // First and second raw moments
    metrics.mean_n = sum_n / d_total;
    double mean_n2 = sum_n2 / d_total;
    metrics.var_n = std::max(0.0, mean_n2 - (metrics.mean_n * metrics.mean_n));

    // Standard error on the mean
    metrics.std_error_mean = std::sqrt(metrics.var_n / d_total);

    // In-sector population & leakage
    uint64_t in_sector_shots = 0;
    auto it_target = metrics.sector_counts.find(target_particles);
    if (it_target != metrics.sector_counts.end()) {
        in_sector_shots = it_target->second;
    }

    metrics.in_sector_population = static_cast<double>(in_sector_shots) / d_total;
    metrics.leakage = 1.0 - metrics.in_sector_population;

    // Binomial standard error on leakage
    metrics.std_error_leakage = std::sqrt((metrics.leakage * (1.0 - metrics.leakage)) / d_total);

    // Asymmetry ratio R_asym = P(w=1) / P(w=3) for 4-qubit registers
    uint64_t c_w1 = metrics.sector_counts[1];
    uint64_t c_w3 = metrics.sector_counts[3];
    if (c_w3 > 0) {
        metrics.asymmetry_ratio = static_cast<double>(c_w1) / static_cast<double>(c_w3);
    } else {
        metrics.asymmetry_ratio = (c_w1 > 0) ? 999.0 : 0.0;
    }

    return metrics;
}

ParityMetrics evaluate_qaoa_parity(
    const std::unordered_map<std::string, uint64_t>& counts
) {
    ParityMetrics metrics;
    if (counts.empty()) {
        return metrics;
    }

    uint64_t total_shots = 0;
    uint64_t even_shots = 0;
    uint64_t odd_shots = 0;

    for (const auto& [bitstring, count] : counts) {
        total_shots += count;
        uint32_t w = fast_hamming_weight(bitstring);
        if ((w & 1) == 0) {
            even_shots += count;
        } else {
            odd_shots += count;
        }
    }

    if (total_shots == 0) {
        return metrics;
    }

    metrics.total_shots = total_shots;
    const double d_total = static_cast<double>(total_shots);

    metrics.positive_population = static_cast<double>(even_shots) / d_total;
    metrics.negative_population = static_cast<double>(odd_shots) / d_total;
    metrics.mean_parity = metrics.positive_population - metrics.negative_population;

    // Standard error on the parity expectation value
    double var_p = std::max(0.0, 1.0 - (metrics.mean_parity * metrics.mean_parity));
    metrics.std_error_parity = std::sqrt(var_p / d_total);

    return metrics;
}

} // namespace algoinvar
