#include <mraa/i2c.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define DEFAULT_PORT 8090

#define COUNTS_TO_DEGREES = (62. / 39212.)

const int I2C_ADDRESS0 = 2;
const int I2C_ADDRESS1 = 3;

void send_update(int sock, double speed, double bearing)
{
	char buf[16];
	sprintf(buf, "%+07.1f,%+07.1f", speed, bearing);
	// send all but the null terminating character
	send(sock, buf, sizeof(buf) - 1, 0);
}

int main(void)
{
    struct sockaddr_in addr, servAddr;
    int sock = 0;
    int port = DEFAULT_PORT;
    
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	error("Socket creation error\n");
    
    servAddr.sin_family = AF_INET;
    servAddr.sin_port = htons(port);
    if (inet_pton(AF_INET, "127.0.0.1", &servAddr.sin_addr) <= 0)
    	error("Invalid address / address not supported\n");
    
    while (connect(sock, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0) {}
    
    printf("Connected to socket!\n");

    const int buf_len = 10;
    char buf[buf_len];

    const int buf_len1 = 10;
    char buf1[buf_len1];

    mraa_i2c_context i2c0 = mraa_i2c_init(0); // Set as master
    mraa_i2c_context i2c1 = mraa_i2c_init(0); // Set as master 
    mraa_i2c_address(i2c0, I2C_ADDRESS0);
    mraa_i2c_address(i2c1, I2C_ADDRESS1);

    while (1) {
        mraa_i2c_read(i2c0, buf, buf_len);
        fprintf(stderr, "I2C0 - Speed: %s\n", buf);
        mraa_i2c_read(i2c1, buf1, buf_len1);
        fprintf(stderr, "I2C1 - Steering: %s\n", buf1);

	double speed = atof(buf);
	double bearing  = atof(buf1);
	double angle = bearing * COUNTS_TO_DEGREES;
        fprintf(stderr, "Steering Angle: %f\n", angle);

	send_update(sock, speed, bearing);

        usleep(200000); // 200ms
    }

    mraa_i2c_stop(i2c0);
    mraa_i2c_stop(i2c1);

    return 0;
}
