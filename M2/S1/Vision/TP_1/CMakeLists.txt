cmake_minimum_required(VERSION 3.12)
set(CMAKE_OSX_ARCHITECTURES "x86_64" CACHE STRING "")
project(Panorama)
list(APPEND CMAKE_FRAMEWORK_PATH /Library/Frameworks) #Mac, why not auto?
find_package(Imagine REQUIRED COMPONENTS LinAlg Images)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(Panorama Panorama.cpp)
target_link_libraries(Panorama Imagine::LinAlg Imagine::Images)
