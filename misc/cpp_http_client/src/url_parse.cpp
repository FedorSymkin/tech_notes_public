#include "url_parse.h"
#include <iostream>


using namespace std;


constexpr int MAX_PROTOCOL_SIZE = 7;
constexpr int DEFAULT_HTTP_PORT = 80;


TDivision ParseProtocol(const string& src)
{
    auto res = DivideBy(src, "://");
    if (!res.Divided || res.First.size() > MAX_PROTOCOL_SIZE) {
        res.First = "http";
        res.Second = src;
    }

    return res;
}

TDivision ParseAddress(const string& src)
{
    auto res = DivideBy(src, "/");

    if (!res.Divided)
        res = DivideBy(src, "?");

    return res;
}

pair<string, int> ParseHostPort(const string& address)
{
    auto res = DivideBy(address, ":");
    if (!res.Divided) {
        return {res.First, DEFAULT_HTTP_PORT};
    }

    return {res.First, std::stoi(res.Second)};
}

void NormalizePath(string& path)
{
    if (path.empty()) {
        path = "/";
        return;
    }

    if (path[0] != '/') {
        path = "/" + path;
    }

    if (path[path.size() - 1] != '/') {
        path = path + "/";
    }
}

TDivision ParsePath(const string& src)
{
    auto res = DivideBy(src, "?");
    NormalizePath(res.First);
    return res;
}


THttpRequest UrlParse(const std::string& url)
{
    /*
     * This is a test code, so url parsing is done more simply than it may be.
     * In real life (depenging on project requirements it may be optimized by
     * avoiding unnecessary copying of strings. For exemple total position pointer may be used
     * without creating new strings.
    */

    THttpRequest res;

    auto protocolAndRest = ParseProtocol(Trimmed(url));
    if (protocolAndRest.First != "http")
        throw std::runtime_error("only http protocol is supported");

    auto addressAndRest = ParseAddress(protocolAndRest.Second);
    std::tie(res.Host, res.Port) = ParseHostPort(addressAndRest.First);

    if (res.Host.empty())
        throw std::runtime_error("empty host, bad url");

    if (addressAndRest.Delimeter == "/") {
        auto pathAndRest = ParsePath(addressAndRest.Second);
        res.Path = pathAndRest.First;
        res.Query = pathAndRest.Second;
    }
    else {
        res.Path = "/";
        res.Query = addressAndRest.Second;
    }

    return res;
}
