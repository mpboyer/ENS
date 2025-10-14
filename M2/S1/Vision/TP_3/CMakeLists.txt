cmake_minimum_required(VERSION 3.12)
project(Seeds)
list(APPEND CMAKE_FRAMEWORK_PATH /Library/Frameworks) #Mac, why not auto?
find_package(Imagine REQUIRED COMPONENTS Images)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(Seeds Seeds.cpp)
target_link_libraries(Seeds Imagine::Images)
