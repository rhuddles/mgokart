#ifndef THROTTLE_CONTROL_H
#define THROTTLE_CONTROL_H

#include <mraa/aio.h>
#include <mraa/pwm.h>

#include <signal.h>

#include "dpdt.h"

extern const int THROTTLE_SIGNAL_ANA;
extern const int THROTTLE_SIGNAL_PWM;

extern const int MANUAL_SWITCH_PIN;

extern const double REFERENCE_VOLTAGE;
extern const int BATTERY_VOLTAGE;

void write_speed(mraa_pwm_context throttle_out, float signal_out);

float read_analog_signal(mraa_aio_context throttle);

#endif
