#ifndef DPDT_H
#define DPDT_H

#include <mraa/gpio.h>
#include <stdlib.h>

/**
 * Usage:
 *  mraa_gpio_context dpdt_pin = init_dpdt();
 *  mraa_gpio_write(dpdt_pin, <[forward|reverse] constant>);
 */

extern const int DPDT_FORWARD;
extern const int DPDT_REVERSE;

/*
 * Create a GPIO context and initialize it to output, initial to FORWARD
 */
extern "C" mraa_gpio_context init_dpdt();

#endif
