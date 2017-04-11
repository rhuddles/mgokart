#include "throttle_control.h"

const int THROTTLE_SIGNAL_ANA = 0;
const int THROTTLE_SIGNAL_PWM = 5;

const int MANUAL_SWITCH_PIN = 9;

const double REFERENCE_VOLTAGE = 5.0;
const int BATTERY_VOLTAGE = 5;

void write_speed(mraa_pwm_context throttle_out, double speed)
{
	float signal_out, volt_out;

	volt_out = (speed + 4.587) / 4.483;
	signal_out = volt_out / REFERENCE_VOLTAGE;

	mraa_pwm_write(throttle_out, signal_out);
}

float read_analog_signal(mraa_aio_context throttle)
{
	float throttle_signal = mraa_aio_read_float(throttle);
	return throttle_signal * REFERENCE_VOLTAGE / BATTERY_VOLTAGE;
}

