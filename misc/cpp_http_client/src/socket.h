#pragma once

#include <common.h>

class ISocket
{
public:
    virtual ~ISocket() = default;
    virtual void Connect(std::string const& host, int port) = 0;
    virtual void Disconnect() = 0;
    virtual void Write(const std::string& data) = 0;
    virtual std::string ReadAllUntilDisconnect() = 0;
};

using TSocketPtr = std::unique_ptr<ISocket>;
using TMakeSocketFunction = std::function<TSocketPtr()>;

TSocketPtr MakeSocket();
