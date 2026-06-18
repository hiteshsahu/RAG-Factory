#include "similarity.hpp"

#include <cmath>

namespace raginator {

std::vector<float> cosine_similarity_batch(
    const std::vector<float>& query,
    const std::vector<std::vector<float>>& candidates) {
    std::vector<float> scores(candidates.size());

    float query_norm = 0.0f;
    for (float v : query) query_norm += v * v;
    query_norm = std::sqrt(query_norm);

    for (size_t i = 0; i < candidates.size(); ++i) {
        const auto& vec = candidates[i];
        float dot = 0.0f, norm = 0.0f;
        for (size_t j = 0; j < vec.size(); ++j) {
            dot += query[j] * vec[j];
            norm += vec[j] * vec[j];
        }
        norm = std::sqrt(norm);
        scores[i] = (query_norm > 0.0f && norm > 0.0f) ? dot / (query_norm * norm) : 0.0f;
    }
    return scores;
}

}  // namespace raginator
