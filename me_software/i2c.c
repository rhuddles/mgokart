#include "i2c.h"

const int I2C_ADDRESS0 = 2;
const int I2C_ADDRESS1 = 3;

void read_from_arduino(mraa_i2c_context i2c, double* data)
{
    const int buf_len = 10;
    char buf[buf_len];

	int result = mraa_i2c_read(i2c, (uint8_t*)buf, buf_len);
	fprintf(stderr, "Result of I2C read %d\n", result);

	*data = atof(buf);
}

