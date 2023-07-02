#include <gtest/gtest.h>
#include <common.h>
#include "http_client.h"
#include "socket.h"


using namespace std;
using TStubResponses = unordered_map<string, string>;


class TStubSocket : public ISocket
{
private:
    string* OutputWrittenData = nullptr;
    TStubResponses StubResponses;
    string WrittenData;

private:
    string GetRequestFirstLine() const
    {
        stringstream ss(WrittenData);
        string line;
        if (!GetLineCrLf(ss, line))
            return "";
        return line;
    }

    void SetWrittenData(const string& data)
    {
        WrittenData = data;
        if (OutputWrittenData)
            *OutputWrittenData = WrittenData;
    }

public:
    TStubSocket(const TStubResponses& stubResponsess, string* outputWrittenData = nullptr)
        : OutputWrittenData(outputWrittenData)
        , StubResponses(stubResponsess)
    {
    }

    void Connect(string const&, int) override
    {
    }

    void Disconnect() override
    {
    }

    void Write(const string& data) override
    {
        SetWrittenData(WrittenData + data);
    }

    string ReadAllUntilDisconnect() override
    {
        string line = GetRequestFirstLine();
        auto it = StubResponses.find(line);
        if (it == StubResponses.end())  {
            cerr << "response for '" << line << "' is not available in stub socket" << endl;
            return "";
        }
        return it->second;

        SetWrittenData("");
    }
};

string MakeResponseText(const string& content, int statusCode = 200, const string& location = "", size_t contentLength = 0)
{
    if (!contentLength)
        contentLength = content.size();

    stringstream ss;
    ss << "HTTP/1.1 " << statusCode << " UNUSED_MSG \r\n"
       << "Server: nginx\r\n"
       << "Content-Length: " << contentLength << "\r\n";

    if (!location.empty())
        ss << "Location: " << location << "\r\n";

    ss << "\r\n"
       << content;

    return ss.str();
}


unique_ptr<ISocket> MakeDefaultTestSocket() {
    auto stubs = TStubResponses({
        {"GET /path/to/resource/?q=1&a=2 HTTP/1.1", MakeResponseText("<html>aaa</html>")},
        {"GET /path/to/resource/ HTTP/1.1", MakeResponseText("<html>bbb</html>")},
        {"GET /path/to/404_resource/?q=1&a=2 HTTP/1.1", MakeResponseText("error", 404)},

        {"GET /redirect_1/ HTTP/1.1", MakeResponseText("", 302, "http://domain.com/redirect_2")},
        {"GET /redirect_2/ HTTP/1.1", MakeResponseText("", 302, "http://domain.com/redirect_3")},
        {"GET /redirect_3/ HTTP/1.1", MakeResponseText("<html>ccc</html>")},

        {"GET /cycle_redirect_1/ HTTP/1.1", MakeResponseText("", 302, "http://domain.com/cycle_redirect_2")},
        {"GET /cycle_redirect_2/ HTTP/1.1", MakeResponseText("", 302, "http://domain.com/cycle_redirect_1")},

        {"GET /bad1/ HTTP/1.1", "trash"},
        {"GET /content_length_greater/ HTTP/1.1", MakeResponseText("ok", 200, "", 10)},
        {"GET /content_length_lower/ HTTP/1.1", MakeResponseText("ok", 200, "", 1)},

        {"GET /empty/ HTTP/1.1", MakeResponseText("")},
    });
    return make_unique<TStubSocket>(stubs);
}


TEST(TestHttpClient, response200query) {
    auto response = HttpGet("http://domain.com/path/to/resource/?q=1&a=2", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 200\nHEADERS:\nContent-Length: 16\nServer: nginx\nCONTENT FACT SIZE: 16");
    ASSERT_EQ(response.Content, "<html>aaa</html>");
}

TEST(TestHttpClient, response200noquery) {
    auto response = HttpGet("http://domain.com/path/to/resource", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 200\nHEADERS:\nContent-Length: 16\nServer: nginx\nCONTENT FACT SIZE: 16");
    ASSERT_EQ(response.Content, "<html>bbb</html>");
}

TEST(TestHttpClient, response200empty) {
    auto response = HttpGet("http://domain.com/empty", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 200\nHEADERS:\nContent-Length: 0\nServer: nginx\nCONTENT FACT SIZE: 0");
    ASSERT_EQ(response.Content, "");
}

TEST(TestHttpClient, response404) {
    auto response = HttpGet("http://domain.com/path/to/404_resource/?q=1&a=2", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 404\nHEADERS:\nContent-Length: 5\nServer: nginx\nCONTENT FACT SIZE: 5");
    ASSERT_EQ(response.Content, "error");
}

TEST(TestHttpClient, response302redirect) {
    auto response = HttpGet("http://domain.com/redirect_1", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 200\nHEADERS:\nContent-Length: 16\nServer: nginx\nCONTENT FACT SIZE: 16");
    ASSERT_EQ(response.Content, "<html>ccc</html>");
}

TEST(TestHttpClient, response302cycleRedirect) {
    ASSERT_THROW(HttpGet("http://domain.com/cycle_redirect_1", MakeDefaultTestSocket), exception);
}

TEST(TestHttpClient, badResp1) {
    ASSERT_THROW(HttpGet("http://domain.com/bad1", MakeDefaultTestSocket), exception);
}

TEST(TestHttpClient, contentLengthGreater) {
    auto response = HttpGet("http://domain.com/content_length_greater", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 200\nHEADERS:\nContent-Length: 10\nServer: nginx\nCONTENT FACT SIZE: 2");
    ASSERT_EQ(response.Content, "ok");
}

TEST(TestHttpClient, contentLengthLower) {
    auto response = HttpGet("http://domain.com/content_length_lower", MakeDefaultTestSocket);
    ASSERT_EQ(response.Info(), "STATUS 200\nHEADERS:\nContent-Length: 1\nServer: nginx\nCONTENT FACT SIZE: 1");
    ASSERT_EQ(response.Content, "o");
}

TEST(TestHttpClient, request) {
    string socketWrittenData;
    auto makeCustomTestSocket = [&socketWrittenData]() -> unique_ptr<ISocket> {
        auto stubs = TStubResponses({
            {"GET /path/to/resource/?q=1&a=2 HTTP/1.1", MakeResponseText("<html>aaa</html>")}
        });
        return make_unique<TStubSocket>(stubs, &socketWrittenData);
    };

    HttpGet("http://domain.com/path/to/resource/?q=1&a=2", makeCustomTestSocket);

    stringstream expected;
    expected << "GET /path/to/resource/?q=1&a=2 HTTP/1.1\r\n"
             << "Host: domain.com\r\n"
             << "Accept: */*\r\n"
             << "User-Agent: test_http_client\r\n"
             << "Connection: close\r\n"
             << "\r\n";

    ASSERT_EQ(socketWrittenData, expected.str());
}
