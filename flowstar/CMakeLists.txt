cmake_minimum_required(VERSION 3.13)
project(flowstar)

set(CMAKE_CXX_STANDARD 14)

include_directories(flowstar-2.1.0)

add_executable(flowstar
        flowstar-2.1.0/Constraints.cpp
        flowstar-2.1.0/Constraints.h
        flowstar-2.1.0/Continuous.cpp
        flowstar-2.1.0/Continuous.h
        flowstar-2.1.0/Geometry.cpp
        flowstar-2.1.0/Geometry.h
        flowstar-2.1.0/Hybrid.cpp
        flowstar-2.1.0/Hybrid.h
        flowstar-2.1.0/include.h
        flowstar-2.1.0/Interval.cpp
        flowstar-2.1.0/Interval.h
        flowstar-2.1.0/lex.yy.c
        flowstar-2.1.0/Matrix.cpp
        flowstar-2.1.0/Matrix.h
        flowstar-2.1.0/modelParser.cpp
        flowstar-2.1.0/modelParser.h
        flowstar-2.1.0/modelParser.tab.c
        flowstar-2.1.0/modelParser.tab.h
        flowstar-2.1.0/Monomial.cpp
        flowstar-2.1.0/Monomial.h
        flowstar-2.1.0/Polynomial.cpp
        flowstar-2.1.0/Polynomial.h
        flowstar-2.1.0/TaylorModel.cpp
        flowstar-2.1.0/TaylorModel.h)
