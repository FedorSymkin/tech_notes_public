#include "common.h"

using namespace std;


EHttpResponseType THttpResponse::Type() const
{
    int group = StatusCode / 100;
    switch (group) {
        case 1: return EHttpResponseType::INFO_1xx;
        case 2: return EHttpResponseType::OK_2xx;
        case 3: return EHttpResponseType::REDIRECT_3xx;
        case 4: return EHttpResponseType::USER_ERROR_4xx;
        case 5: return EHttpResponseType::SERVER_ERROR_5xx;
        default: return EHttpResponseType::UNKNOWN;
    }
}

bool THttpResponse::IsOK() const
{
    return Type() == EHttpResponseType::OK_2xx;
}

string THttpResponse::Info() const
{
    string res = "STATUS " + to_string(StatusCode) + "\n";
    res += "HEADERS:\n";

    map<string, string> sortedHeaders(Headers.begin(), Headers.end());
    for (const auto& h: sortedHeaders)
        res += h.first + ": " + h.second + "\n";

    res += "CONTENT FACT SIZE: " + to_string(Content.size());
    return res;
}

string THttpResponse::GetHeader(const string& header, bool required) const
{
    auto it = Headers.find(header);
    if (it == Headers.end()) {
        if (required)
            throw runtime_error("header " + header + " is required");
        return "";
    }

    return it->second;
}

size_t THttpResponse::GetContentLength() const
{
    string contentLengthText = GetHeader("Content-Length", false);
    if (contentLengthText.empty())
        return 0;

    try {
        return std::stol(contentLengthText);
    }
    catch (const exception& e) {
        throw runtime_error("bad content length header: " + contentLengthText + ", error: " + string(e.what()));
    }
}

bool StartsWith(const string& s, const string& with)
{
    return s.find(with) == 0;
}

string Trimmed(const string& s)
{
    size_t first = s.find_first_not_of(" ");
    size_t last = s.find_last_not_of(" ");
    if (first == string::npos || last == string::npos || first >= last)
        return "";

    return s.substr(first, last - first + 1);
}

TDivision DivideBy(const string& src, const string& delimeter)
{
    TDivision res;

    size_t found = src.find(delimeter);
    if (found == string::npos) {
        res.First = src;
        return res;
    }

    res.First = src.substr(0, found);
    res.Second = src.substr(found + delimeter.size(), src.size() - found - delimeter.size());
    res.Divided = true;
    res.Delimeter = delimeter;

    return res;
}

bool GetLineCrLf(istream& in, string& line)
{
    bool res = bool(std::getline(in, line));
    if (!res)
        return false;

    if (line.empty())
        return true;

    if (line[line.size() - 1] == '\r')
        line.resize(line.size() - 1);

    return true;
}
