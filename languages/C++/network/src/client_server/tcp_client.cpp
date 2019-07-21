// http://masandilov.ru/network/guide_to_network_programming
#include "common.h"
#include "sockets.h"


using namespace std;


TEST(network, simple_tcp_client) {
    // Как проверить - запустить simple_tcp_server_fork, а потом запустить этот тест
    // Больше подробностей как работать с сокетами в примере simple_tcp_server_fork

    string host = "localhost"; //здесь, в отличие от сервера назначаем host
    string port = "3490";
    auto addrinfo = TAddrInfo(host, port, ETransportProtocol::TCP);
    addrinfo.AssertValid();

    std::unique_ptr<TSocket> socket;
    for (const auto& addr: addrinfo) {
        socket = std::make_unique<TSocket>(addr);
        if (!socket->IsValid()) {
            continue;
        }

        // На стороне клиента вместо bind будет connect
        if (!socket->Connect(addr)) {
            continue;
        }

        break;
    }
    if (!socket)
        throw std::runtime_error("could not create socket");

    cout << "connected to " << socket->GetRemoteAddr() << endl;
    cout << "data received: " << socket->Recv() << endl;
}

