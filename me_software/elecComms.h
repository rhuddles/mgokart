#ifndef ELECCOMMS_H
#define ELECCOMMS_H

#include <arpa/inet.h>
#include <mraa/uart.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define UART_BUFFER_SIZE 6

extern mraa_uart_context uart;

extern "C" void get_commands(int sock, double* speed, double* bearing);

extern "C" void send_update(int sock, double speed, double bearing);

extern "C" int open_socket(int port);

#endif
