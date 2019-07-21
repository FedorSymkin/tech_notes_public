#include "common.h"

using namespace std;

// http://masandilov.ru/network/guide_to_network_programming



TEST(network, example_select_one_stdin) {
    //Ждём один файловый дескриптор - stdin

    cout << "=====example_select_one_stdin====" << endl;

    #define STDIN 0

    struct timeval tv;
    tv.tv_sec = 2;
    tv.tv_usec = 500000;
    cout << "sizeof(timeval) = " << sizeof(timeval) << endl;  //sizeof(timeval) = 16


    // fd_set - это хитрая сишная конструкция, которая по сути представляет собой список файловых дескрипторов.
    // На C++ мы бы написали что-то вроде readfds.AddFd(STDIN);
    fd_set readfds;
    FD_ZERO(&readfds);
    FD_SET(STDIN, &readfds);
    cout << "sizeof(fd_set) = " << sizeof(fd_set) << endl; //sizeof(fd_set) = 128

    /*
     * int select(int numfds, fd_set *readfds, fd_set *writefds, fd_set *exceptfds, struct timeval *timeout);
     *
     * numfds - это не количество файловых дескрипторов как может показаться, а самый большой fd из списка + 1. Такая вот упячка
     * readfds, writefds, exceptfds - это мы отдельно можем ждать чтения, записи, и ошибок.
     * В данном случае ждём только чтения
     */
    select(STDIN+1, &readfds, NULL, NULL, &tv);


    // Если просигналил какой-то fd (в данном случае STDIN) тогда он останется в наборе readfds, иначе пропадёт.
    // Сторку (FD_ISSET(STDIN, &readfds)) на С++ мы бы написали типа такого: if (readfds.Contains(STDIN))
    if (FD_ISSET(STDIN, &readfds))
        cout << "Has input" << endl;
    else
        cout << "Timed out" << endl;
}


struct TPipes
{
    std::vector<int> Fds;
    bool Initialized = false;

    TPipes(size_t count)
    {
        try {
            if (count < 1 || count >10) {
                throw std::runtime_error("bad count");
            }

            system("rm -rf ./example_select_two_pipes_tmp");
            system("mkdir ./example_select_two_pipes_tmp");

            for (size_t i = 0; i < count; ++i) {
                string pipePath = "./example_select_two_pipes_tmp/pipe" + std::to_string(i);
                cout << "make pipe " << pipePath << endl;
                mkfifo(pipePath.c_str(), 0666);
            }

            cout << "opening pipes" << endl;

            for (size_t i = 0; i < count; ++i) {
                string pipePath = "./example_select_two_pipes_tmp/pipe" + std::to_string(i);
                int fd = open(pipePath.c_str(), 0);
                if (fd <= 0) {
                    throw std::runtime_error("error opening pipe");
                }
                Fds.push_back(fd);
                cout << "opened pipe: " << pipePath << ", fd=" << fd << endl;
            }

            Initialized = true;
        }
        catch (const std::exception& e) {
            cerr << e.what() << endl;
        }
    }

    ~TPipes()
    {
        for (auto fd: Fds) {
            if (fd) {
                close(fd);
                cout << "closed pipe: " << fd << endl;
            }
        }
    }

    void Assert() const
    {
        if (!Initialized)
            throw std::runtime_error("TPipes error");
    }

    int MaxFd() const
    {
        return *std::max_element(Fds.begin(), Fds.end());
    }
};


TEST(network, example_select_two_pipes) {
    /*
        Ждём несколько файловых дескрипторов (пайпы) и читаем из них.
        Также демонстрируется чтение из пайпов с использованием FIONREAD (т.е. читаем столько байт, сколько пришло)

        Как с этим работать:
            * Запустить тест, он залипнет на открытии пайпов
            * Открыть пайпы с другой стороны в отдельных консолях (читаем stdin и перенаправляем в пайп):
                * cat - > example_select_two_pipes_tmp/pipe0
                * cat - > example_select_two_pipes_tmp/pipe1
            * Тест напишет opened pipe, и перейдёт к waiting...
            * Пишем в пайпы что-нибудь, видим как данные получены в тесте
            * При выходе из cat пайп с той стороны закрывается, и тест завершится.
    */

    cout << "=====example_select_two_pipes====" << endl;

    TPipes pipes(2);
    pipes.Assert();

    while (true) {
        cout << "waiting..." << endl;

        fd_set readfds;
        FD_ZERO(&readfds);
        for (auto fd: pipes.Fds) {
            FD_SET(fd, &readfds);
        }

        //засыпаем в ожидании любого из пайпов
        select(pipes.MaxFd() + 1, &readfds, NULL, NULL, NULL);

        for (auto fd: pipes.Fds) {
            if (FD_ISSET(fd, &readfds)) {

                //В пайпе fd есть данные. Прочитаем их. Для этого воспользуемся ioctl с опцией FIONREAD -
                //узнать сколько байт доступно для чтения
                int nread = 0;
                if (ioctl(fd, FIONREAD, &nread) < 0) throw std::runtime_error("ioctl error");
                if (nread < 0) throw std::runtime_error("nread < 0 ");

                if (nread == 0) {
                    //Если пайп просигналил и 0 байт доступно к чтению, значит он закрыт с той стороны -> выходим
                    cout << "end" << endl;
                    return;
                }

                //просто как обычно читаем полученное количество байт
                string data;
                data.resize(nread);
                read(fd, data.data(), nread);
                cout << "got from fd " << fd << ": " << data << endl;
            }
        }
    }
}
