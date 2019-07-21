// http://masandilov.ru/network/guide_to_network_programming
#include "common.h"
#include "sockets.h"


using namespace std;


TEST(network, simple_udp_server) {
    // Как проверить - запустить simple_udp_server, а потом через simple_udp_client

    // UDP-сервер здесь понятие условное. В данном примере не устанавливается соединение, поэтому
    // это только называется сервер, а по сути - программа, которая принимает датаграммы
    // Больше подробностей как работать с сокетами в примере simple_tcp_server_fork

    string port = "3490";
    auto addrinfo = TAddrInfo("", port, ETransportProtocol::UDP);
    addrinfo.AssertValid();

    std::unique_ptr<TSocket> socket;
    for (const auto& addr: addrinfo) {
        socket = std::make_unique<TSocket>(addr);
        if (!socket->IsValid()) {
            continue;
        }

        if (!socket->Bind(addr)) {
            continue;
        }

        break;
    }
    if (!socket)
        throw std::runtime_error("could not create socket");

    // Тут, в отличие от TCP нет понятий слушающего сокета, listen и accept - соединение не устанавливается,
    // а просто читаем из сокета, который забиндили, как из пайпа

    cout << "waiting udp packets on port " << port << endl;
    while (true) {
        //Важно что здесь remote address приходит вместе с данными
        auto datagram = socket->RecvDatagram();
        cout << "received datagram from " << datagram.RemoteAddr << ": " << datagram.Data << endl;
    }
}
