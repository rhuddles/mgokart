#include "dpdt.h"

#include <unistd.h>

/**
 * For testing all the modules
 */

int main(void)
{
    // Initialize pins
    mraa_gpio_context dpdt_pin = init_dpdt();

    // Set DPDT to reverse then forward
    mraa_gpio_write(dpdt_pin, DPDT_REVERSE);
    usleep(100000000); // 1 second
    mraa_gpio_write(dpdt_pin, DPDT_FORWARD);

    // Close pins
    mraa_gpio_close(dpdt_pin);

    return 0;
}
