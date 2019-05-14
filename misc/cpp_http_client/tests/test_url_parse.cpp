#include <gtest/gtest.h>
#include "url_parse.h"

using namespace std;

void UrlParseTestCase(const string& url, const string& expexted)
{
    string fact = UrlParse(url).Print();
    ASSERT_EQ(expexted, fact);
}

TEST(TestUrlParsePositive, main) {
    UrlParseTestCase("http://domain.com", "http://domain.com:80/");
    UrlParseTestCase("domain.com", "http://domain.com:80/");
    UrlParseTestCase("http://domain.com/", "http://domain.com:80/");
    UrlParseTestCase("http://domain.com:8080", "http://domain.com:8080/");
    UrlParseTestCase("http://domain.com:8080/", "http://domain.com:8080/");
    UrlParseTestCase("http://domain.com?q=1", "http://domain.com:80/?q=1");
    UrlParseTestCase("http://domain.com/?q=1", "http://domain.com:80/?q=1");
    UrlParseTestCase("http://domain.com/path/to/resource", "http://domain.com:80/path/to/resource/");
    UrlParseTestCase("http://domain.com/path/to/resource/", "http://domain.com:80/path/to/resource/");
    UrlParseTestCase("http://domain.com/path/to/resource?aa=bb&cc=dd", "http://domain.com:80/path/to/resource/?aa=bb&cc=dd");
    UrlParseTestCase("http://domain.com/path/to/resource/?aa=bb&cc=dd", "http://domain.com:80/path/to/resource/?aa=bb&cc=dd");
    UrlParseTestCase("http://domain.com/path/to/resource?aa=bb&cc=http://aaa", "http://domain.com:80/path/to/resource/?aa=bb&cc=http://aaa");
    UrlParseTestCase("localhost", "http://localhost:80/");
}

TEST(TestUrlParseThrows, main) {
    ASSERT_THROW(UrlParse("https://domain.com"), std::exception);
    ASSERT_THROW(UrlParse("http://?bla-bla"), std::exception);
    ASSERT_THROW(UrlParse("http://domain.com:aaaa"), std::exception);
    ASSERT_THROW(UrlParse("http://"), std::exception);
    ASSERT_THROW(UrlParse(""), std::exception);
}
