#include <mraa/aio.h>
#include <mraa/pwm.h>

#include <signal.h>

#include "dpdt.h"

const int THROTTLE_SIGNAL_ANA = 0;
const int THROTTLE_SIGNAL_PWM = 5;

const int MANUAL_SWITCH_PIN = 9;

const int REFERENCE_VOLTAGE = 5;
const int BATTERY_VOLTAGE = 5;

int running = 1;

void stop_running(int signal);

// If manual we read from accelerator's analog signal
// If not we read from electrical team's m/s command

float read_analog_signal(mraa_aio_context throttle);
float read_mps();

int main(void)
{
	// Set DPDT
	mraa_gpio_context dpdt_pin = init_dpdt();
	mraa_gpio_write(dpdt_pin, DPDT_FORWARD);

	// Init GPIO
	mraa_gpio_context manual_switch = mraa_gpio_init(MANUAL_SWITCH_PIN);
	mraa_gpio_dir(manual_switch, MRAA_GPIO_IN);

	// Init Analog
	mraa_aio_context throttle_in = mraa_aio_init(THROTTLE_SIGNAL_ANA);

	// Init PWM
	mraa_pwm_context throttle_out = mraa_pwm_init(THROTTLE_SIGNAL_PWM);
	mraa_pwm_period_us(throttle_out, 50);	
	mraa_pwm_enable(throttle_out, 1);

	signal(SIGINT, stop_running);                                               
	signal(SIGABRT, stop_running);

	while (running) {
		// Check if manual or autonomous
		int manual = mraa_gpio_read(manual_switch);

		float signal_out;

		// Read Analog
		if (manual) {
		    fprintf(stderr, "Autonomous Mode\n");
		    signal_out = read_mps();
		}
		// Read m/s
		else {
		    fprintf(stderr, "Manual Mode\n");
		    signal_out = read_analog_signal(throttle_in);
		}

		// Write PWM
		mraa_pwm_write(throttle_out, signal_out);
		fprintf(stderr, "Write %f to pin %d\n\n", signal_out, THROTTLE_SIGNAL_PWM);

		usleep(1000000);
	}

	mraa_gpio_close(manual_switch);

	mraa_aio_close(throttle_in);

	fprintf(stderr, "\nClosing...\n");
	fprintf(stderr, "Write 0 to pin %d\n", THROTTLE_SIGNAL_PWM);
	mraa_pwm_write(throttle_out, 0);
	mraa_pwm_close(throttle_out);

	return 0;
}

void stop_running(int signal)
{
	running = 0;
}

float read_analog_signal(mraa_aio_context throttle)
{
	float throttle_signal = mraa_aio_read_float(throttle);
	fprintf(stderr, "Read %f from pin %d\n", throttle_signal, THROTTLE_SIGNAL_ANA);

	return throttle_signal * REFERENCE_VOLTAGE / BATTERY_VOLTAGE;
}

float read_mps()
{
	// Based on 9V reference
	// Want about 3V
	return 0.33;
}
