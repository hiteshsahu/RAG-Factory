#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "similarity.hpp"

namespace py = pybind11;

PYBIND11_MODULE(raginator_native, m) {
    m.doc() = "RAG-Factory native acceleration module (CPU/CUDA)";
    m.def("cosine_similarity_batch", &raginator::cosine_similarity_batch,
          py::arg("query"), py::arg("candidates"),
          "Cosine similarity between a query vector and a batch of candidate vectors.");
}
