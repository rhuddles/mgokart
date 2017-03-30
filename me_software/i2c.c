#include <mraa/i2c.h>
#include <unistd.h>

const int I2C_ADDRESS0 = 2;
const int I2C_ADDRESS1 = 3;

int main(void)
{
    const int buf_len = 6;
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
        usleep(200000); // 200ms
    }

    mraa_i2c_stop(i2c0);
    mraa_i2c_stop(i2c1);

    return 0;
}
