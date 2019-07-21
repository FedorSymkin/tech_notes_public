// http://masandilov.ru/network/guide_to_network_programming
#include "common.h"
#include "sockets.h"


using namespace std;


TEST(network, simple_udp_client) {
    // Как проверить - запустить simple_udp_server, а потом через simple_udp_client

    // UDP-клиент здесь понятие условное. В данном примере не устанавливается соединение, поэтому
    // это только называется клиент, а по сути - программа, которая отправляет датаграммы
    // Больше подробностей как работать с сокетами в примере simple_tcp_server_fork

    //Важная осбенность: датаграммы не гарантируют получение, поэтому
    //если сервер не поднят - датаграмма просто уйдёт в никуда, и здесь ничего не упадёт

    string host = "localhost";
    string port = "3490";
    auto addrinfo = TAddrInfo(host, port, ETransportProtocol::UDP);
    addrinfo.AssertValid();

    std::unique_ptr<TSocket> socket;
    struct addrinfo remoteAddr;
    for (const auto& addr: addrinfo) {
        socket = std::make_unique<TSocket>(addr);
        if (!socket->IsValid()) {
            continue;
        }

        // Никакого connect!

        remoteAddr = addr;
        break;
    }
    if (!socket)
        throw std::runtime_error("could not create socket");

    socket->SendDatagram(remoteAddr, "hello world");
}
