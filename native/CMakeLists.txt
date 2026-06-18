cmake_minimum_required(VERSION 3.18)
project(raginator_native LANGUAGES CXX)

option(USE_CUDA "Build CUDA-accelerated kernels instead of the CPU fallback" OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 CONFIG REQUIRED)

set(NATIVE_SOURCES
    src/similarity.cpp
    bindings/bindings.cpp
)

if(USE_CUDA)
    enable_language(CUDA)
    list(REMOVE_ITEM NATIVE_SOURCES src/similarity.cpp)
    list(APPEND NATIVE_SOURCES src/similarity_cuda.cu)
endif()

pybind11_add_module(raginator_native ${NATIVE_SOURCES})
target_include_directories(raginator_native PRIVATE include)

if(USE_CUDA)
    set_target_properties(raginator_native PROPERTIES CUDA_SEPARABLE_COMPILATION ON)
    target_link_libraries(raginator_native PRIVATE CUDA::cudart)
endif()
