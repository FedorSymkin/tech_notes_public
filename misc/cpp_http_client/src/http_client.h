#pragma once

#include "common.h"
#include "socket.h"

THttpResponse HttpGet(const std::string& url, const TMakeSocketFunction& makeSocketFunc = MakeSocket);
