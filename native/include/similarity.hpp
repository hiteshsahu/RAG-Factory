#pragma once

#include <vector>

namespace ragfactory {

// Cosine similarity between a single query vector and a batch of candidate
// vectors. Returns one score per candidate. Implemented in similarity.cpp
// (CPU) or similarity_cuda.cu (CUDA), selected at build time by USE_CUDA.
std::vector<float> cosine_similarity_batch(
    const std::vector<float>& query,
    const std::vector<std::vector<float>>& candidates);

}  // namespace ragfactory
