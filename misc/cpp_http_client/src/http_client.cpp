#include "http_client.h"
#include "common.h"
#include "url_parse.h"


using namespace std;


class THttpClient
{
    static constexpr int MAX_REDIRECT_LEVEL = 10;
    static constexpr size_t MAX_CONTENT_LENTH = 1024 * 1024 * 100;

private:
    const TMakeSocketFunction MakeSocketFunc;

private:
    int ReadHttpCode(istream& in) const
    {
        string line;
        if (!GetLineCrLf(in, line))
            throw runtime_error("no data");

        line = Trimmed(line);

        if (!StartsWith(line, "HTTP/1"))
            throw runtime_error("bad first line of response: " + line);

        auto left = DivideBy(line, " ");
        if (!left.Divided)
            throw runtime_error("bad first line of response: " + line);

        auto right = DivideBy(left.Second, " ");
        if (!right.Divided)
            throw runtime_error("bad first line of response: " + line);

        try {
            return std::stoi(right.First);
        }
        catch (const exception& e) {
            throw runtime_error("could not parse http code from response, error " + string(e.what()));
        }
    }

    TDivision ExtractHeader(const string& line) const
    {
        auto division = DivideBy(line, ": ");
        if (!division.Divided)
            throw runtime_error("bad header line: " + line);

        return division;
    }

    void ReadHeaders(istream& in, THttpResponse& res) const
    {
        string line;
        while (GetLineCrLf(in, line)) {
            line = Trimmed(line);
            if (line.empty())
                break;

            auto header = ExtractHeader(line);
            res.Headers[header.First] = header.Second;
        }
    }

    string FetchData(const THttpRequest& request) const
    {
        /*
         * This is a test code, so downloading is in whole-block style.
         * Depending on real life task it would be streaming downloading,
         * for example using circular buffer and stream-like class around it.
         *
         * In real life I would think and compare, what resource is more valuable
         * in terms of current situation - to do it more quickly or to do it more
         * productive in memory and CPU
        */

        auto socket = MakeSocketFunc();
        socket->Connect(request.Host, request.Port);

        string resource = request.Path;
        if (!request.Query.empty())
            resource += "?" + request.Query;

        stringstream requestContent;
        requestContent << "GET " << resource << " HTTP/1.1\r\n"
                       << "Host: " << request.Host << "\r\n"
                       << "Accept: */*\r\n"
                       << "User-Agent: test_http_client\r\n"
                       << "Connection: close\r\n"
                       << "\r\n";

        socket->Write(requestContent.str());
        return socket->ReadAllUntilDisconnect();
    }

public:
    THttpResponse Get(const string &url, int redirectLevel = 0) const
    {
        THttpResponse res;
        cerr << "GET '" << url << "'" << endl;

        if (redirectLevel > MAX_REDIRECT_LEVEL)
            throw runtime_error("too long redirects cycle");

        THttpRequest request = UrlParse(url);
        stringstream responseStream(FetchData(request));

        res.StatusCode = ReadHttpCode(responseStream);
        ReadHeaders(responseStream, res);

        switch (res.Type()) {
            case EHttpResponseType::UNKNOWN:
                throw runtime_error("Unknown response type");

            case EHttpResponseType::INFO_1xx:
                throw runtime_error("INFO_1xx response is not supported");

            case EHttpResponseType::REDIRECT_3xx:
                return Get(res.GetHeader("Location"), redirectLevel + 1);

            default:
                break;
        }

        size_t contentLength = res.GetContentLength();
        if (contentLength > MAX_CONTENT_LENTH)
            throw runtime_error("too big content length: " + to_string(contentLength));

        if (contentLength) {
            res.Content.resize(contentLength);
            size_t readCnt = responseStream.readsome(&res.Content[0], contentLength);
            res.Content.resize(readCnt);
        }

        return res;
    }

    THttpClient(const TMakeSocketFunction& makeSocketFunc)
        : MakeSocketFunc(makeSocketFunc)
    {}
};


THttpResponse HttpGet(const string& url, const TMakeSocketFunction& makeSocketFunc)
{
    return THttpClient(makeSocketFunc).Get(url);
}
