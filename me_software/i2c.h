#ifndef I2C_H
#define I2C_H

#include <arpa/inet.h>
#include <mraa/i2c.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#define COUNTS_TO_DEGREES (62. / 39212.)

extern const int I2C_ADDRESS0;
extern const int I2C_ADDRESS1;

extern "C" int read_from_arduino(mraa_i2c_context i2c0, double* data);

#endif
