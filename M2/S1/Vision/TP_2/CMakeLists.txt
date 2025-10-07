cmake_minimum_required(VERSION 3.5)
set(CMAKE_OSX_ARCHITECTURES "x86_64" CACHE STRING "") #Apple Silicon
project(Fundamental)
list(APPEND CMAKE_FRAMEWORK_PATH /Library/Frameworks) #Mac, why not auto?
find_package(Imagine REQUIRED COMPONENTS LinAlg Images)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(Fundamental
        Fundamental.cpp
        Imagine/SIFT_VL.cpp
        Imagine/vl/generic.c Imagine/vl/host.c Imagine/vl/imop.c Imagine/vl/sift.c)
target_link_libraries(Fundamental Imagine::LinAlg Imagine::Images)
