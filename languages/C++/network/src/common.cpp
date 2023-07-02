#include "common.h"

std::string GetThreadId()
{
    std::stringstream ss;
    ss << std::this_thread::get_id();
    return ss.str();
}

void CError(const std::string& err)
{
    perror(err.data());
    throw std::runtime_error(err);
}

void SigchldHandler(int)
{
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

void SetAntiZombieSigHandler()
{
    static struct sigaction sa;
    sa.sa_handler = SigchldHandler; // обрабатываем мёртвые процессы
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1)
        CError("sigaction");
}
