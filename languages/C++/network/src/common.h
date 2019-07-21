#pragma once

#include <string>
#include <sstream>
#include <vector>
#include <iostream>
#include <deque>
#include <thread>

#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>

#include <fcntl.h>
#include <algorithm>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <signal.h>

#include <gtest/gtest.h>



std::string GetThreadId();
void CError(const std::string& err);
void SetAntiZombieSigHandler();
