#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <thread>
#include <mutex>

#include <mraa/uart.h>

#define DEFAULT_PORT 8090
#define UART_BUFFER_SIZE 6

bool running = true;
double SPEED = 0;
double BEARING = 0;

mraa_uart_context uart;

void error(const char * const msg)
{
	perror(msg);
	exit(0);
}

void get_commands(int sock)
{
	int errno;
	char speed[5], bearing[5], buf[12];
	while (running)
	{
		//errno = read(sock, buf, sizeof(buf));
		
		memcpy(speed, buf, 5);
		memcpy(bearing, buf+6, 5);
		SPEED = atof(speed);
		BEARING = atof(bearing);
		//printf("Speed:\t\t%+5.1f\n", SPEED);
		//printf("Bearing:\t%+5.1f\n\n", BEARING);
	}
}

void send_update(int sock, double speed, double bearing)
{
	char buf[16];
	sprintf(buf, "%+07.1f,%+07.1f", speed, bearing);
	// send all but the null terminating character
	send(sock, buf, sizeof(buf) - 1, 0);
}

// sock is the socket to throw state updates into
void get_state_updates(int sock)
{
	char buf[UART_BUFFER_SIZE];

	while (running) {
		int recvd = mraa_uart_read(uart, buf, UART_BUFFER_SIZE);
		if (recvd != UART_BUFFER_SIZE) {
			continue;
		}

		int val = atoi(buf);
		printf("Bearing: %d\n", val);
		send_update(sock, 500.0, (double) val);
	}
}

int main(int argc, char** argv)
{
	struct sockaddr_in addr, servAddr;
	int sock = 0;
	int port = DEFAULT_PORT;
	char buf[1024] = {0};
	double speed = 2.3, bearing = -10;

	if (argc >= 2)
		port = atoi(argv[1]);

	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
		error("Socket creation error\n");

	uart = mraa_uart_init(0);

	if (uart == NULL) {
		printf("UART failed to setup\n");
		return 1;
	}

	mraa_uart_set_baudrate(uart, 115200);
	
	servAddr.sin_family = AF_INET;
	servAddr.sin_port = htons(port);
	if (inet_pton(AF_INET, "127.0.0.1", &servAddr.sin_addr) <= 0)
		error("Invalid address / address not supported\n");

	while (connect(sock, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0) {}

	printf("Connected to socket!\n");

	std::thread t1(get_commands, sock);
	std::thread t2(get_state_updates, sock);

	t1.join();
	t2.join();
	return 0;
}
