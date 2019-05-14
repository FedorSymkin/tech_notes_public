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
    "src/socket.cpp"
    "src/http_client.cpp"
    "src/url_parse.cpp"
    "src/common.cpp"
)

set(HEADERS_CPP
    "src/socket.h"
    "src/http_client.h"
    "src/url_parse.cpp"
    "src/common.h"
)

add_executable(cpp_http_client "src/main.cpp" ${SOURCE_CPP} ${HEADERS_CPP})
# target_link_libraries(cpp_http_client ${GTEST_LIBRARIES})

enable_testing()

set(TEST_SOURCE_CPP
    "tests/test_main.cpp"
    "tests/test_common.cpp"
    "tests/test_url_parse.cpp"
    "tests/test_http_client.cpp"
)

set(TEST_HEADERS_CPP

)

add_executable( tests ${SOURCE_CPP} ${TEST_SOURCE_CPP} ${HEADERS_CPP} ${TEST_HEADERS_CPP} )
target_link_libraries(tests ${GTEST_LIBRARIES} pthread)
add_test( tests tests )
