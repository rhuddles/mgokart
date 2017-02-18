# Setup CXXFLAGS
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")

cmake_minimum_required(VERSION 2.8)

project( main )

find_package(OpenCV REQUIRED )
find_package(Qt5Core REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

add_executable( trainer trainer.cpp )

target_link_libraries( trainer
		${OpenCV_LIBS}
		${Boost_PROGRAM_OPTIONS_LIBRARY}
		Qt5::Core
		)
