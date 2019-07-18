#include <iostream>
#include <gtest/gtest.h>

#include "json.h"


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

    std::stringstream input;
    input << std::cin.rdbuf();
    std::string data = input.str();

    auto jsonObject = NJson::Parse(data);
    std::cout << jsonObject->Print() << std::endl;

    return 0;
}
