#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../include/algoinvar_fast.hpp"

namespace py = pybind11;

PYBIND11_MODULE(algoinvar_core, m) {
    m.doc() = "AlgoInvar High-Performance C++ Core Engine: Hardware-accelerated bitwise invariant evaluators";

    // Bind FockMetrics struct
    py::class_<algoinvar::FockMetrics>(m, "FockMetrics", "Container for VQE Fock-space particle-number metrics")
        .def_readonly("mean_n", &algoinvar::FockMetrics::mean_n, "Expectation value <N>")
        .def_readonly("var_n", &algoinvar::FockMetrics::var_n, "Particle-number variance Var(N)")
        .def_readonly("std_error_mean", &algoinvar::FockMetrics::std_error_mean, "Standard error of the mean")
        .def_readonly("in_sector_population", &algoinvar::FockMetrics::in_sector_population, "Preserved in-sector fraction")
        .def_readonly("leakage", &algoinvar::FockMetrics::leakage, "Out-of-sector probability mass")
        .def_readonly("std_error_leakage", &algoinvar::FockMetrics::std_error_leakage, "Binomial error of leakage")
        .def_readonly("asymmetry_ratio", &algoinvar::FockMetrics::asymmetry_ratio, "Population asymmetry ratio P(w=1)/P(w=3)")
        .def_readonly("total_shots", &algoinvar::FockMetrics::total_shots, "Total evaluated shot volume")
        .def_readonly("sector_counts", &algoinvar::FockMetrics::sector_counts, "Raw shot distribution by Hamming weight");

    // Bind ParityMetrics struct
    py::class_<algoinvar::ParityMetrics>(m, "ParityMetrics", "Container for QAOA global Z2 spin-parity metrics")
        .def_readonly("mean_parity", &algoinvar::ParityMetrics::mean_parity, "Global parity expectation <P>")
        .def_readonly("std_error_parity", &algoinvar::ParityMetrics::std_error_parity, "Standard error on parity")
        .def_readonly("positive_population", &algoinvar::ParityMetrics::positive_population, "Even parity sector fraction")
        .def_readonly("negative_population", &algoinvar::ParityMetrics::negative_population, "Odd parity sector fraction")
        .def_readonly("total_shots", &algoinvar::ParityMetrics::total_shots, "Total evaluated shot volume");

    // Expose core diagnostic functions
    m.def("fast_hamming_weight", &algoinvar::fast_hamming_weight,
          py::arg("bitstring"),
          "Fast hardware-optimized population count for bitstrings");

    m.def("evaluate_fock_distribution", &algoinvar::evaluate_fock_distribution,
          py::arg("counts"), py::arg("target_particles") = 2,
          "Evaluates VQE particle conservation and leakage across measurement counts");

    m.def("evaluate_qaoa_parity", &algoinvar::evaluate_qaoa_parity,
          py::arg("counts"),
          "Evaluates QAOA global Z2 spin-parity expectation value across transversal X counts");
}
