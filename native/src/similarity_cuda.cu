#include <cuda_runtime.h>

#include <algorithm>
#include <cmath>

#include "similarity.hpp"

namespace ragfactory {

namespace {

__global__ void cosine_similarity_kernel(const float* query, const float* candidates,
                                          float* scores, int dim, int num_candidates,
                                          float query_norm) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= num_candidates) return;

    const float* vec = candidates + static_cast<size_t>(i) * dim;
    float dot = 0.0f, norm = 0.0f;
    for (int j = 0; j < dim; ++j) {
        dot += query[j] * vec[j];
        norm += vec[j] * vec[j];
    }
    norm = sqrtf(norm);
    scores[i] = (query_norm > 0.0f && norm > 0.0f) ? dot / (query_norm * norm) : 0.0f;
}

}  // namespace

std::vector<float> cosine_similarity_batch(
    const std::vector<float>& query,
    const std::vector<std::vector<float>>& candidates) {
    const int dim = static_cast<int>(query.size());
    const int num_candidates = static_cast<int>(candidates.size());

    std::vector<float> flat(static_cast<size_t>(num_candidates) * dim);
    for (int i = 0; i < num_candidates; ++i) {
        std::copy(candidates[i].begin(), candidates[i].end(),
                   flat.begin() + static_cast<size_t>(i) * dim);
    }

    float query_norm = 0.0f;
    for (float v : query) query_norm += v * v;
    query_norm = std::sqrt(query_norm);

    float *d_query, *d_candidates, *d_scores;
    cudaMalloc(&d_query, dim * sizeof(float));
    cudaMalloc(&d_candidates, flat.size() * sizeof(float));
    cudaMalloc(&d_scores, num_candidates * sizeof(float));

    cudaMemcpy(d_query, query.data(), dim * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_candidates, flat.data(), flat.size() * sizeof(float), cudaMemcpyHostToDevice);

    const int threads = 256;
    const int blocks = (num_candidates + threads - 1) / threads;
    cosine_similarity_kernel<<<blocks, threads>>>(d_query, d_candidates, d_scores, dim,
                                                    num_candidates, query_norm);

    std::vector<float> scores(num_candidates);
    cudaMemcpy(scores.data(), d_scores, num_candidates * sizeof(float), cudaMemcpyDeviceToHost);

    cudaFree(d_query);
    cudaFree(d_candidates);
    cudaFree(d_scores);
    return scores;
}

}  // namespace ragfactory
