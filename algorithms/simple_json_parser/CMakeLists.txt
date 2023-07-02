cmake_minimum_required(VERSION 3.5)

project (simple_json_parser)

set(CMAKE_CACHEFILE_DIR, "build")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -g")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED on)

find_package(GTest REQUIRED)

include_directories(
    src
    SYSTEM
    ${GTEST_INCLUDE_DIRS}
)

set(SOURCE_CPP
"src/main.cpp"
"src/helpers.cpp"
"src/json.cpp"
"src/tests.cpp"
)

set(HEADERS_CPP
"src/helpers.h"
"src/json.h"
)

add_executable(simple_json_parser ${SOURCE_CPP} ${HEADERS_CPP})

set(LINK_LIBS ${GTEST_LIBRARIES} pthread)

target_link_libraries(simple_json_parser ${LINK_LIBS})

