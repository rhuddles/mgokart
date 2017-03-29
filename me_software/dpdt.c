#include "dpdt.h"

#include <stdlib.h>

const int DPDT_PIN = 3;

const int DPDT_FORWARD = 0;
const int DPDT_REVERSE = 1;

mraa_gpio_context init_dpdt()
{
	mraa_gpio_context dpdt_pin = mraa_gpio_init(DPDT_PIN);
	mraa_gpio_dir(dpdt_pin, MRAA_GPIO_OUT_LOW);
    return dpdt_pin;
}
