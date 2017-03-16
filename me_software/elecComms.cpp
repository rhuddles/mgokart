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

bool running = true;
double SPEED = 0;
double BEARING = 0;

void error(char* msg)
{
	perror(msg);
	exit(0);
}

void get_updates(int sock)
{
	int errno;
	char speed[5], bearing[5], buf[12];
	while (running)
	{
		errno = read(sock, buf, sizeof(buf));

		memcpy(speed, buf, 5);
		memcpy(bearing, buf+6, 5);
		SPEED = atof(speed);
		BEARING = atof(bearing);
		printf("Speed: %f\n", SPEED);
		printf("Bearing: %f\n", BEARING);
	}
}

void send_updates(int sock, double speed, double bearing)
{
	char buf[12];
	sprintf(buf, "%+05.1f,%+05.1f", speed, bearing);
	send(sock, buf, sizeof(buf), 0);
}

int main(int argc, char** argv)
{
	struct sockaddr_in addr, servAddr;
	int sock = 0;
	char buf[1024] = {0};
	double speed = 2.3, bearing = -10;

	if (argc < 2)
		error("No port number given\n");

	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
		error("Socket creation error\n");

	servAddr.sin_family = AF_INET;
	servAddr.sin_port = htons(atoi(argv[1]));
	if (inet_pton(AF_INET, "127.0.0.1", &servAddr.sin_addr) <= 0)
		error("Invalid address / address not supported\n");

	if (connect(sock, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0)
		error("Connection failed\n");

	std::thread t(get_updates, sock);

	send_updates(sock, 4.3, -14.2);

	t.join();
	return 0;
}
