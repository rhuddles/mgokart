#include <mraa/aio.h>
#include <mraa/pwm.h>

const int DPDT_PIN = 3;

const int THROTTLE_SIGNAL_ANA = 0;
const int THROTTLE_SIGNAL_PWM = 5;

const int REFERENCE_VOLTAGE = 5; // 5 Volts
const int BATTERY_VOLTAGE = 9; // 9 Volts

int main(void)
{
	//
	mraa_gpio_context dpdt_pin = mraa_gpio_init(DPDT_PIN);
	mraa_gpio_dir(dpdt_pin, MRAA_GPIO_OUT);
	
	mraa_gpio_write(dpdt_pin, 0);
	// --

	// Init Analog
	mraa_aio_context throttle_in = mraa_aio_init(THROTTLE_SIGNAL_ANA);

	// Init PWM
	mraa_pwm_context throttle_out = mraa_pwm_init(THROTTLE_SIGNAL_PWM);
	mraa_pwm_period_us(throttle_out, 50);	
	mraa_pwm_enable(throttle_out, 1);
	
	while (1) {
		// Read Analog
		float throttle_signal = mraa_aio_read_float(throttle_in);
		float throttle_voltage = throttle_signal * REFERENCE_VOLTAGE;
		fprintf(stderr, "Read %f from pin %d\n", throttle_signal, THROTTLE_SIGNAL_ANA);
		fprintf(stderr, "Read %fV from pin %d\n", throttle_voltage, THROTTLE_SIGNAL_ANA);

		// Write PWM
		float signal_out = throttle_signal * REFERENCE_VOLTAGE / BATTERY_VOLTAGE;
		mraa_pwm_write(throttle_out, signal_out);
		fprintf(stderr, "Write %f to pin %d\n\n", signal_out, THROTTLE_SIGNAL_PWM);

		usleep(1000000);
	}

	mraa_aio_close(throttle_in);

	mraa_pwm_write(throttle_out, 0);
	mraa_pwm_close(throttle_out);
}

