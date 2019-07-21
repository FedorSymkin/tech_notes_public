cmake_minimum_required(VERSION 3.5)

project (network)

set(CMAKE_CACHEFILE_DIR, "build")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -g")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED on)

find_package(GTest REQUIRED)

include_directories(
    src
    src/example_select
    SYSTEM
    ${GTEST_INCLUDE_DIRS}
)

set(SOURCE_CPP
"src/main.cpp"
"src/common.cpp"
"src/example_select/example_select.cpp"
"src/client_server/tcp_server.cpp"
"src/client_server/tcp_client.cpp"
"src/client_server/udp_server.cpp"
"src/client_server/udp_client.cpp"
"src/client_server/sockets.h"
)

set(HEADERS_CPP
"src/common.h"
)

add_executable(network ${SOURCE_CPP} ${HEADERS_CPP})

set(LINK_LIBS ${GTEST_LIBRARIES} pthread)

target_link_libraries(network ${LINK_LIBS})

