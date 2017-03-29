#include <mraa/i2c.h>
#include <unistd.h>

const int I2C_ADDRESS = 2;

int main(void)
{
    const int buf_len = 6;
    char buf[buf_len];

    mraa_i2c_context i2c = mraa_i2c_init(0); // Set as master

    mraa_i2c_address(i2c, I2C_ADDRESS);

    while (1) {
        mraa_i2c_read(i2c, buf, buf_len);
        fprintf(stderr, "Speed: %s\n", buf);
        usleep(200000); // 200ms
    }

    mraa_i2c_stop(i2c);

    return 0;
}
