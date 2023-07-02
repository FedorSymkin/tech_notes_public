#pragma once

#include <string>
#include <map>
#include <unordered_map>
#include <sstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <functional>
#include <memory>

struct THttpRequest
{
    std::string Host;
    int Port = 0;
    std::string Path;
    std::string Query;

    std::string Print() const
    {
        std::stringstream ss;
        ss << "http://" << Host << ":" << Port << Path;
        if (!Query.empty())
            ss << "?" << Query;

        return ss.str();
    }
};

enum class EHttpResponseType
{
    UNKNOWN,
    INFO_1xx,
    OK_2xx,
    REDIRECT_3xx,
    USER_ERROR_4xx,
    SERVER_ERROR_5xx,
};

struct THttpResponse
{
    using THeaders = std::unordered_map<std::string, std::string>;

    std::string Content;
    THeaders Headers;
    int StatusCode = 0;

    EHttpResponseType Type() const;
    bool IsOK() const;
    std::string Info() const;

    std::string GetHeader(const std::string& header, bool required = true) const;
    size_t GetContentLength() const;
};

struct TDivision
{
    std::string First;
    std::string Second;
    bool Divided = false;
    std::string Delimeter;
};

TDivision DivideBy(const std::string& src, const std::string& delimeter);
bool StartsWith(const std::string& s, const std::string &with);
std::string Trimmed(const std::string& s);
bool GetLineCrLf(std::istream& in, std::string& line);
