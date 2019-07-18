#include <gtest/gtest.h>
#include <fstream>

#include "json.h"

// Это

std::string ReadFile(const std::string& filename)
{
    std::ifstream f(filename);
    if (!f.is_open())
        throw std::runtime_error("file not found: " + filename);

    std::stringstream input;
    input << f.rdbuf();
    return input.str();
}


void SaveFile(const std::string& filename, const std::string& data)
{
    std::ofstream f(filename);

    if (!f.is_open())
        throw std::runtime_error("cannot open file for writing: " + filename);

    f.write(data.data(), data.size());
}


std::string Sample(const std::string& data)
{
    static size_t maxSize = 128;

    if (data.size() > maxSize)
        return data.substr(0, maxSize) + "...";
    else
        return data;
}


void TestWithSuccess(const std::string& data)
{
    // compare my output with jq output
    system("mkdir -p tmp");

    auto jsonObject = NJson::Parse(data);
    std::string my = jsonObject->Print();

    SaveFile("tmp/my.json", my);
    SaveFile("tmp/src.json", data);
    system("cat tmp/my.json | jq --sort-keys . > tmp/my_jq.json");
    system("cat tmp/src.json | jq --sort-keys . > tmp/src_jq.json");

    std::string myJq = ReadFile("tmp/my_jq.json");
    std::string srcJq = ReadFile("tmp/src_jq.json");

    if (myJq != srcJq) {
        std::cerr << "difference with jq on data: " << Sample(data) << std::endl;
        FAIL();
    }

    std::cout << "OK: " << Sample(my) << std::endl;
}


void TestWithFail(const std::string& data)
{
    bool wasFail = false;

    try {
        NJson::Parse(data);
    }
    catch (const std::exception& e) {
        wasFail = true;
    }

    if (!wasFail) {
        std::cerr << "parsing was not failed on data: " << Sample(data) << std::endl;
        FAIL();
    }

    std::cout << "OK (failied as expected): " << Sample(data) << std::endl;
}


TEST(json_parser, simple) {
    TestWithSuccess("{\"aa\": \"bb\", \"cc\": \"dd\"}");
    TestWithSuccess("{}");
    TestWithSuccess("{   }");
}


TEST(json_parser, from_file) {
    TestWithSuccess(ReadFile("test_data/1.json"));
}


TEST(json_parser, fails) {
    TestWithFail("{   ");
    TestWithFail("{\"1\": \"2\"} bla bla");
    TestWithFail("{\"1\": }");
    TestWithFail("{\"1\": 56}");
    TestWithFail("{\"1dfdf}");
    TestWithFail("{\"a\": [}");
    TestWithFail("{\"a\": \"\\y\"}");
    TestWithFail("[\"a\"]");
    TestWithFail("\"hello\"");
}
