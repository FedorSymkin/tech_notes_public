#include <iostream>
#include <gtest/gtest.h>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--ut") {
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

    std::cout << "Hello world!" << std::endl;
    return 0;
}
