#include "i2c.h"

const int I2C_ADDRESS0 = 2;
const int I2C_ADDRESS1 = 3;

void read_from_arduinos(mraa_i2c_context i2c0, mraa_i2c_context i2c1,
		double* speed, double* bearing)
{
    const int buf_len = 10;
    const int buf_len1 = 10;
    char buf[buf_len];
    char buf1[buf_len1];

	mraa_i2c_read(i2c0, buf, buf_len);
	mraa_i2c_read(i2c1, buf1, buf_len1);

	*speed = atof(buf);
	*bearing = atof(buf1);
}

