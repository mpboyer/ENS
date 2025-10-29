cmake_minimum_required(VERSION 3.10)
set(CMAKE_OSX_ARCHITECTURES "x86_64" CACHE STRING "") #Apple Silicon
project(GraphCuts)
list(APPEND CMAKE_FRAMEWORK_PATH /Library/Frameworks) #Mac, why not auto?
find_package(Imagine REQUIRED COMPONENTS Images)
set(CMAKE_CXX_STANDARD 11)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# add_executable(exampleGC exampleGC.cpp maxflow/graph.cpp)
add_executable(GCDisparity GCDisparity.cpp maxflow/graph.cpp)
target_link_libraries(GCDisparity Imagine::Images)
