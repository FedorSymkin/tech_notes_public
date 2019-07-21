/*
http://masandilov.ru/network/guide_to_network_programming

Сетевое программирование на С/С++ больше похоже на С, и код выглядит несколько стрёмно.

Здесь сишные вещи инкапсулированы в классы так, чтобы с одной стороны код был читаемым, с другой стороны каждый класс
соответствал одному сишному понятию в сетевом программировании, т.е. степень инкапсуляции не самая глубокая,
чтобы из кода были понятны основные конепции и стадии.
*/


#pragma once
#include "common.h"


enum class ETransportProtocol {TCP, UDP};


class TAddrInfo {
private:
    const std::string Host;
    const std::string Port;
    const ETransportProtocol Protocol;

private:
    bool Valid = false;
    struct addrinfo* Result = nullptr;

private:
    struct addrinfo MakeHints() const
    {
        struct addrinfo hints;
        memset(&hints, 0, sizeof hints);
        hints.ai_family = AF_UNSPEC; // не важно, IPv4 или IPv6

        switch (Protocol) {
            case ETransportProtocol::TCP: hints.ai_socktype = SOCK_STREAM; break;
            case ETransportProtocol::UDP: hints.ai_socktype = SOCK_DGRAM; break;
            default: throw std::runtime_error("unknown protocol");
        }

        if (Host.empty()) {
            // если не задан хост, значит это сервер, и тогда надо флаг, что использовать
            // какой-нибудь ip из существующих на машине
            hints.ai_flags = AI_PASSIVE;
        }

        return hints;
    }

    struct addrinfo* MakeResult(const struct addrinfo& hints) const
    {
        struct addrinfo* result = nullptr;

        int retval = getaddrinfo(
            Host.empty() ? NULL : Host.data(),
            Port.data(),
            &hints,
            &result
        );

        if (retval != 0)
            CError("getaddrinfo");

        return result;
    }

public:
    TAddrInfo(const std::string& host, const std::string& port, const ETransportProtocol protocol)
        : Host(host)
        , Port(port)
        , Protocol(protocol)
    {
        try {
            struct addrinfo hints = MakeHints();
            Result = MakeResult(hints);
            Valid = true;
        } catch (const std::exception& e) {
            std::cerr << e.what() << std::endl;
        }
    }

    ~TAddrInfo() {
        if (Result) {
            freeaddrinfo(Result);
            Result = nullptr;
        }
    }

    void AssertValid() const
    {
        if (!Valid)
            throw std::runtime_error("addrinfo was not initialized");
    }

public:

    // addrinfo - это связной список, потому что на машине может быть несколько сетей и несколько ip-адресов,
    // соответственно сокет при подготовке данных для работы с сокетом адресов выдаётся несколько.
    class TIterator {
    private:
        struct addrinfo* Pos = nullptr;

    public:
        TIterator(struct addrinfo* pos) : Pos(pos) {}

        const struct addrinfo& operator*() const {
            if (!Pos)
                throw std::runtime_error("TAddrInfo iterator empty");
            return *Pos;
        }

        void operator++() {
            if (Pos && Pos->ai_next)
                Pos = Pos->ai_next;
            else
                Pos = nullptr;
        }

        bool operator==(const TIterator& other) const {
            return Pos == other.Pos;
        }

        bool operator!=(const TIterator& other) const {
            return !(*this == other);
        }
    };

    TIterator begin() const {
        return TIterator(Result);
    }

    TIterator end() const {
        return TIterator(nullptr);
    }
};


class TSocket
{
private:
    int Fd = 0;
    bool Valid = false;
    std::string RemoteAddr;

private:
    static void* GetInAddr(const struct sockaddr *sa)
    {
        // Вспомогательная ф-ция только для удобвства работы с сишными структурами
        if (sa->sa_family == AF_INET) {
            return &(((struct sockaddr_in*)sa)->sin_addr);
        }
        else {
            return &(((struct sockaddr_in6*)sa)->sin6_addr);
        }
    }

    static std::string MakeRemoteAddr(const sockaddr_storage& sockAddrStorage)
    {
        // Всякая грязная работа с сишными структурами просто, чтобы получить строку адреса
        try {
            struct sockaddr* sa = (struct sockaddr *)&sockAddrStorage;
            void *pAddr = GetInAddr(sa);
            char res[INET6_ADDRSTRLEN];
            inet_ntop(sockAddrStorage.ss_family, pAddr, res, sizeof(res));
            return std::string(res);
        }
        catch (const std::exception& e) {
            std::cerr << e.what() << std::endl;
            return  "";
        }
    }

    static std::string MakeRemoteAddr(const struct addrinfo& addrInfo)
    {
        // Всякая грязная работа с сишными структурами просто, чтобы получить строку адреса
        try {
            void *pAddr = GetInAddr(addrInfo.ai_addr);
            char res[INET6_ADDRSTRLEN];
            inet_ntop(addrInfo.ai_family, pAddr, res, sizeof(res));
            return std::string(res);
        }
        catch (const std::exception& e) {
            std::cerr << e.what() << std::endl;
            return  "";
        }
    }

public:
    TSocket(const struct addrinfo& addr)
    {
        // Создаём новый сокет в системе
        try {
            Fd = socket(addr.ai_family, addr.ai_socktype, addr.ai_protocol);
            if (Fd == -1)
                CError("socket");

            //Это опция, чтобы при бинке сокет пробовал ещё раз через некоторое время забиндиться, если порт занят
            static int yes = 1;
            if (setsockopt(Fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1)
                CError("setsockopt");

            Valid = true;
        } catch (const std::exception& e) {
            std::cerr << e.what() << std::endl;
        }
    }

    TSocket(const int fd, const sockaddr_storage& theirAddr)
        : Fd(fd)
        , RemoteAddr(MakeRemoteAddr(theirAddr))
    {
        // Используем уже созданный сокет, полученный из accept
        Valid = true;
    }

    ~TSocket()
    {
        if (Fd) {
            std::cout << "pid" << getpid() << " tid" << GetThreadId() << " closing fd " << Fd << std::endl;
            close(Fd);
            Fd = 0;
        }
    }

    void AssertValid()
    {
        if (!Valid || !Fd)
            throw std::runtime_error("addrinfo was not initialized");
    }

    void AssertHasRemoteAddr()
    {
        if (RemoteAddr.empty())
            throw std::runtime_error("socket has not permanent connection to remote");
    }

    bool IsValid()
    {
        return Valid;
    }

    bool Bind(const struct addrinfo& addr)
    {
        AssertValid();

        try {
            if (bind(Fd, addr.ai_addr, addr.ai_addrlen) == -1)
                CError("bind");

            return true;
        }
        catch (...) {
            return false;
        }
    }

    bool Connect(const struct addrinfo& addr)
    {
        AssertValid();

        try {
            if (connect(Fd, addr.ai_addr, addr.ai_addrlen) == -1)
                CError("connect");

            RemoteAddr = MakeRemoteAddr(addr);
            return true;
        }
        catch (...) {
            return false;
        }
    }

    void Listen(int maxPendingCount)
    {
        AssertValid();

        if (listen(Fd, maxPendingCount) == -1)
            CError("listen");
    }

    std::unique_ptr<TSocket> Accept()
    {
        //Для сервера: слушающий сокет при accept-е создаёт новый клиентский сокет, через который уже идёт обмен
        AssertValid();

        struct sockaddr_storage theirAddr;
        socklen_t sinSize = sizeof(theirAddr);

        int newFd = accept(Fd, (struct sockaddr *)&theirAddr, &sinSize);
        if (newFd == -1)
            CError("accept");

        return std::make_unique<TSocket>(newFd, theirAddr);
    }

    std::string GetRemoteAddr()
    {
        AssertValid();
        AssertHasRemoteAddr();
        return RemoteAddr;
    }

    void Send(const std::string& data)
    {
        //Обращаю внимание, что здесь не реализована доотправка, если отправно не всё. В реальной жизни надо это учесть.

        AssertValid();

        if (send(Fd, data.data(), data.size(), 0) == -1)
            CError("send");
    }

    std::string Recv()
    {
        // Важная тонкость: в recv будут получено столько байт, сколько сейчас доступно для чтения.
        // Т.е. MAXDATASIZE - это не количество желаемых байт, а просто размер буфера для чтения.
        // Если recv вернулся и получено 0 байт - значит соединение закрыто с той стороны.

        AssertValid();
        AssertHasRemoteAddr();

        int numbytes = 0;
        static int MAXDATASIZE = 4096;
        char buf[MAXDATASIZE];

        if ((numbytes = recv(Fd, buf, MAXDATASIZE-1, 0)) == -1)
            CError("recv");

        buf[numbytes] = 0;
        return std::string(buf);
    }

    struct TDatagram
    {
        std::string RemoteAddr;
        std::string Data;
    };

    TDatagram RecvDatagram()
    {
        // Отличие от обычного recv в том, что получение данных идёт без соединения -
        // просто получаем от любого кто отправит на наш хост/порт
        // Поэтому здесь, в отличие от обычного recv сразу отдаётся адрес, откуда пришла датаграмма

        AssertValid();

        TDatagram res;

        struct sockaddr_storage theirAddr;
        socklen_t sinSize = sizeof(theirAddr);

        int numbytes = 0;
        static int MAXBUFLEN = 4096;
        char buf[MAXBUFLEN];

        if ((numbytes = recvfrom(Fd, buf, MAXBUFLEN - 1 , 0, (struct sockaddr *)&theirAddr, &sinSize)) == -1)
           CError("recvfrom");

        res.Data = std::string(buf);
        res.RemoteAddr = MakeRemoteAddr(theirAddr);
        return res;
    }

    void SendDatagram(const struct addrinfo& addr, const std::string& data)
    {
        // Аналогично send, но:
        //     * Здесь же передаётся и адрес, куда слать, потому что нет предварительного connect
        //     * Если та сторона не примет (сервер не поднят или что-то ещё) - здесь ничего не изменится,
        //          потому что нет гарантий получения

        AssertValid();

        if (sendto(Fd, data.data(), data.size(), 0, addr.ai_addr, addr.ai_addrlen) == -1)
            CError("sendto");
    }
};

