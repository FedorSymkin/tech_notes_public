#include "common.h"

//http://masandilov.ru/network/guide_to_network_programming

int main(int argc, char **argv) {
    /*
    sudo apt-get install libgtest-dev

    cd /usr/src/gtest
    sudo cmake CMakeLists.txt
    sudo make
    sudo cp *.a /usr/lib
    */
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
