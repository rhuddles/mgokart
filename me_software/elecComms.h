#ifndef ELECCOMMS_H
#define ELECCOMMS_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <mraa/uart.h>

#define UART_BUFFER_SIZE 6

mraa_uart_context uart;

void get_commands(int sock, double* speed, double* bearing);

void send_update(int sock, double speed, double bearing);

int open_socket(int port);

#endif
