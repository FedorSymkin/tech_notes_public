cmake_minimum_required(VERSION 3.5)

project (cpp_http_client)

set(CMAKE_CACHEFILE_DIR, "build")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -g")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED on)
                     
find_package(GTest REQUIRED)

include_directories(
    src
    SYSTEM
)

set(SOURCE_CPP
    "src/main.cpp"
    "src/socket.cpp"
)

set(HEADERS_CPP
    "src/socket.h"
)

add_executable(cpp_http_client ${SOURCE_CPP} ${HEADERS_CPP})
target_link_libraries(cpp_http_client ${GTEST_LIBRARIES})

