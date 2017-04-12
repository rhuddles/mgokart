#include "elecComms.h"

void get_commands(int sock, double* speed, double* bearing)
{
	int errno;
	char speed_tmp[5], bearing_tmp[5], buf[12];

	errno = read(sock, buf, sizeof(buf));

	memcpy(speed_tmp, buf, 5);
	memcpy(bearing_tmp, buf+6, 5);

	*speed = atof(speed_tmp);
	*bearing = atof(bearing_tmp);
	printf("Recv: %+07.1f,%+07.1f\n", *speed, *bearing);
}

void send_update(int sock, double speed, double bearing)
{
	char buf[16];
	sprintf(buf, "%+07.1f,%+07.1f", speed, bearing);
	// send all but the null terminating character
	fprintf(stderr, "Sending bearing of %s\n", buf);
	send(sock, buf, 15*sizeof(char), 0);
}

int open_socket(int port)
{
	struct sockaddr_in addr, servAddr;
	int sock = 0;

	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		fprintf(stderr, "Socket creation error\n");
		return -1;
	}

	servAddr.sin_family = AF_INET;
	servAddr.sin_port = htons(port);
	if (inet_pton(AF_INET, "127.0.0.1", &servAddr.sin_addr) <= 0)
	{
		fprintf(stderr, "Invalid address / address not supported\n");
		return -1;
	}

	while (connect(sock, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0);

	return sock;
}

