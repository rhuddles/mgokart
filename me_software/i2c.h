#ifndef I2C_H
#define I2C_H

#include <mraa/i2c.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define COUNTS_TO_DEGREES (62. / 39212.)

extern const int I2C_ADDRESS0;
extern const int I2C_ADDRESS1;

void read_from_arduinos(mraa_i2c_context i2c0, mraa_i2c_context i2c1,
		double* speed, double* bearing);

#endif
