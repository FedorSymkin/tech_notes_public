#include <iostream>
#include <string>

extern "C" {

void hello(const char *name) {
    std::cout << "hello " << std::string(name) << std::endl;
}

}

