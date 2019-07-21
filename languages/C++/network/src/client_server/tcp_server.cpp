// http://masandilov.ru/network/guide_to_network_programming
#include "common.h"
#include "sockets.h"



using namespace std;


TEST(network, simple_tcp_server_fork) {
    //Как проверить - запустить сервер, а потом через telnet
    //В этом примере детально расписаны стадии, в других примерах будет похожий код, уже без лишних комментариев



    // Готовимся к созданию сервера
    string port = "3490"; // port строкой потому что можно указать ещё например "http" - и умная OS поймёт, что это 80
    string host = ""; // Хост не указываем, потому что это сервер. Внутри TAddrInfo стоит флаг - взять любой доступный ip
                      // на этой машине
    auto addrinfo = TAddrInfo(host, port, ETransportProtocol::TCP);
    addrinfo.AssertValid();



    // Делаем слушающий сокет. Его назначение - только получить входящее соединение и отдать его в виде нового сокета.
    // Addrinfo - это связной список ip, на которые можно повесить сервер. Ведь внутри одной машины
    // может быть несколько ip и несколько сетей.
    // Мы обходим этот список в попытке создать и забиндить сокет на каком-нибудь ip
    std::unique_ptr<TSocket> listenSocket;
    for (const auto& addr: addrinfo) {

        //Здесь из addr берётся только мета-инфа о протоколе, типе сокета и т.д., но пока не хост-порт
        listenSocket = std::make_unique<TSocket>(addr);
        if (!listenSocket->IsValid()) {
            continue;
        }

        // Понятие бинда - привязываем сокет к хосту-порту
        if (!listenSocket->Bind(addr)) {
            continue;
        }

        break;
    }
    if (!listenSocket)
        throw std::runtime_error("could not create listenSocket");


    // Приказываем слушающему сокету начать слушать входящие соединения
    // и говорим, что максимум их в очереди может скопиться 10 ожидающих соединений.
    // Факитически, когда мы потом говорим Accept, мы либо берём из очереди уже полученное входящее соединение,
    // либо спим пока там, что-нибудь не появится.
    // Если пришло соединение, но очередь забита - клиент получит от ворот поворот.
    cout << "listening on port " << port << endl;
    listenSocket->Listen(10);




    // Мы потом будем форкаться. Это просто обработчик сигнала, чтобы считывать код возврата дочерних процессов,
    // чтобы не плодить зомби
    SetAntiZombieSigHandler();





    cout << "waiting for connections..." << endl;
    while (true) {  //выходим просто по sigint (ctrl+C)

        //Здесь засыпаем в ожидании соединения. Слушающий сокет вернёт нам newSocket, в который уже будем
        //отвечать hello world
        std::unique_ptr<TSocket> newSocket = listenSocket->Accept();
        cout << "conection from " << newSocket->GetRemoteAddr() << endl;

        if (!fork()) {
            //дочерний процесс

            //Слушающий сокет дочернему процессу не нужен - закрываем его.
            // Важно понимать, что на уровне ОС сокет не закрывается, потому что его дескриптор открыт в родительском процессе.
            // Такой же принцип как с shared_ptr
            listenSocket.reset();

            //Шлём ответ, закрываем сокет, завершаемся
            newSocket->Send("hello world");
            newSocket.reset();
            exit(0);
        }

        // Родительскому процессу сокет для обмена даными не нужен - закрываем его, и идём слушать дальше.
        // Важно понимать, что на уровне ОС сокет не закрывается, потому что его дескриптор открыт в дочернем процессе.
        // Такой же принцип как с shared_ptr
        newSocket.reset();
    }
}


TEST(network, simple_tcp_server_multithread) {
    //Как проверить - запустить сервер, а потом через telnet
    // Аналогично simple_tcp_server_fork, но многопоточно.
    // Больше подробностей как работать с сокетами в примере simple_tcp_server_fork

    string port = "3490";
    auto addrinfo = TAddrInfo("", port, ETransportProtocol::TCP);
    addrinfo.AssertValid();

    std::unique_ptr<TSocket> listenSocket;
    for (const auto& addr: addrinfo) {
        listenSocket = std::make_unique<TSocket>(addr);
        if (!listenSocket->IsValid()) {
            continue;
        }

        if (!listenSocket->Bind(addr)) {
            continue;
        }

        break;
    }
    if (!listenSocket)
        throw std::runtime_error("could not create listenSocket");



    cout << "listening on port " << port << endl;
    listenSocket->Listen(10);



    cout << "waiting for connections..." << endl;
    while (true) {
        std::unique_ptr<TSocket> newSocket = listenSocket->Accept();
        cout << "conection from " << newSocket->GetRemoteAddr() << endl;

        const auto threadFunc = [](std::unique_ptr<TSocket>&& socket){
            socket->Send("hello world");
            socket.reset();
            cout << "end of connection thread\n";
        };
        std::thread(threadFunc, std::move(newSocket)).detach();
    }
}


class TSocketBufferWrapper
{
//класс вокруг сокета, чтобы делать ReadLine через буфер
private:
    TSocket& Socket;
    string Buff;

public:
    TSocketBufferWrapper(TSocket& socket, size_t buffSize = 4096)
        : Socket(socket)
    {
        Buff.reserve(buffSize);
    }

    bool ReadLine(std::string& line)
    {
        while (true) {
            size_t found = Buff.find('\n');
            if (found != string::npos) {
                line = Buff.substr(0, found - 1);
                Buff.erase(0, found + 1);
                return true;
            }

            string newData = Socket.Recv();
            if (newData.empty())
                return false;
            Buff += newData;
        }
    }
};

TEST(network, simple_tcp_server_multithread_readline) {
    // Как проверить - запустить сервер, а потом через telnet
    // Сервер, которые читает данные line-by-line
    // Больше подробностей как работать с сокетами в примере simple_tcp_server_fork

    string port = "3490";
    auto addrinfo = TAddrInfo("", port, ETransportProtocol::TCP);
    addrinfo.AssertValid();

    std::unique_ptr<TSocket> listenSocket;
    for (const auto& addr: addrinfo) {
        listenSocket = std::make_unique<TSocket>(addr);
        if (!listenSocket->IsValid()) {
            continue;
        }

        if (!listenSocket->Bind(addr)) {
            continue;
        }

        break;
    }
    if (!listenSocket)
        throw std::runtime_error("could not create listenSocket");

    cout << "listening on port " << port << endl;
    listenSocket->Listen(10);


    cout << "waiting for connections..." << endl;
    while (true) {
        std::unique_ptr<TSocket> newSocket = listenSocket->Accept();
        cout << "conection from " << newSocket->GetRemoteAddr() << endl;

        const auto threadFunc = [](std::unique_ptr<TSocket>&& socket){
            TSocketBufferWrapper bufferedSocket(*socket);
            std::string line;
            while (bufferedSocket.ReadLine(line)) {
                cout << "got line: '" << line << "'" << endl;
            }
            socket.reset();
            cout << "end of connection thread\n";
        };
        std::thread(threadFunc, std::move(newSocket)).detach();
    }
}
