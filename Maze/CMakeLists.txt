cmake_minimum_required (VERSION 2.8)
project(maze)
list(APPEND CMAKE_CXX_FLAGS "-pthread -std=c++11 ${CMAKE_CXX_FLAGS}")

add_executable(maze maze.cpp piwars.cpp Robot.cpp Utils.cpp)
