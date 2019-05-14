#include "socket.h"

#include <sys/socket.h>
#include <errno.h>
#include <iostream>
#include <unistd.h>
#include <string.h>
#include <netdb.h>


using namespace std;


class TSocket : public ISocket
{
    static constexpr size_t SOCKET_READ_PORTION = 4096;

private:
    int Sockfd = 0;
    bool Connected = false;

private:
    void AssertConnected() const
    {
        if (!Connected || !Sockfd) {
            throw runtime_error("socket wasn't conected");
        }
    }

public:
    void Connect(const string& host, int port) override
    {
        if (Sockfd)
            return;

        Sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (Sockfd < 0)
            throw runtime_error("Error opening socket: " + to_string(errno));

        //There is no memory leak here:
        //https://stackoverflow.com/questions/11544411/how-does-gethostbyname-return-struct-hostent-without-requiring-the-caller
        struct hostent *server = gethostbyname(host.c_str());

        if (server == NULL)
            throw runtime_error("Error resolving host: " + to_string(errno));

        struct sockaddr_in servAddr;
        memset((void*) &servAddr, 0, sizeof(servAddr));
        servAddr.sin_family = AF_INET;
        servAddr.sin_port = htons(port);
        memcpy((void*) &servAddr.sin_addr.s_addr, (void*) server->h_addr, server->h_length);

        if (connect(Sockfd, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0)
            throw runtime_error("Error connecting to host: " + to_string(errno));

        Connected = true;
    }

    void Disconnect() override
    {
        if (!Connected || !Sockfd)
            return;

        close(Sockfd);
        Sockfd = 0;
        Connected = false;
    }

    ~TSocket() override
    {
        Disconnect();
    }

    void Write(const string& data) override
    {
        AssertConnected();
        if (data.empty())
            return;

        size_t n = write(Sockfd, data.data(), data.size());
        if (n != data.size()) {
            stringstream msg;
            msg << "Error writing data socket,"
                << " expected written size: " << data.size()
                << " fact written size: " + n;

            throw runtime_error(msg.str());
        }
    }

    string ReadAllUntilDisconnect() override
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

        AssertConnected();

        string res;
        string buff;
        buff.resize(SOCKET_READ_PORTION);

        while (int cnt = read(Sockfd, &buff[0], SOCKET_READ_PORTION)) {
            if (cnt < 0) {
                throw runtime_error("error reading socket");
            }

            size_t oldsize = res.size();
            res.resize(res.size() + cnt);
            memcpy(&res[oldsize], buff.data(), cnt);
        }

        return res;
    }
};

unique_ptr<ISocket> MakeSocket()
{
    return make_unique<TSocket>();
}
