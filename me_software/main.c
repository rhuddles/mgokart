#include "dpdt.h"
#include "elecComms.h"
#include "throttle_control.h"
#include "i2c.h"
#include "stepper.h"

#include <unistd.h>

#define DEFAULT_PORT 8090

int running = 1;

/**
 * For testing all the modules
 */

void stop_running(int signal)
{
	running = 0;
}

int main(void)
{
	char buf[1024] = {0};
	int sock = 0, autonomous;
	double target_speed = 0, target_bearing = 0;
	double real_speed = 0, real_bearing = 0;
	float signal_out, volt_out;

	signal(SIGINT, stop_running);
	signal(SIGABRT, stop_running);

    // Init DPDT
    mraa_gpio_context dpdt_pin = init_dpdt();

	// Init GPIO
	mraa_gpio_context manual_switch = mraa_gpio_init(MANUAL_SWITCH_PIN);
	mraa_gpio_dir(manual_switch, MRAA_GPIO_IN);

	// Init Analog
	mraa_aio_context throttle_in = mraa_aio_init(THROTTLE_SIGNAL_ANA);

	// Init PWM
	mraa_pwm_context throttle_out = mraa_pwm_init(THROTTLE_SIGNAL_PWM);
	mraa_pwm_period_us(throttle_out, 50);
	mraa_pwm_enable(throttle_out, 1);

	// Init I2C
    mraa_i2c_context i2c0 = mraa_i2c_init(0); // Set as master
    mraa_i2c_context i2c1 = mraa_i2c_init(0); // Set as master
    mraa_i2c_address(i2c0, I2C_ADDRESS0);
    mraa_i2c_address(i2c1, I2C_ADDRESS1);

	// Init Stepper Motor
	CPhidgetStepperHandle stepper = setup_stepper();

    // Set DPDT to reverse then forward
    mraa_gpio_write(dpdt_pin, DPDT_FORWARD);


	sock = open_socket(DEFAULT_PORT);
	if (sock == -1)
	{
		fprintf(stderr, "Error: could not open socket");
		return 1;
	}

	while (running)
	{
		// Check if manual or autonomous
		autonomous = mraa_gpio_read(manual_switch);
		if (autonomous) {
			// edits speed and bearing to be the targets
			get_commands(sock, &target_speed, &target_bearing);

			volt_out = (target_speed + 4.587) / 4.483;
			signal_out = volt_out / 5.0;
		}
		else {
		    signal_out = read_analog_signal(throttle_in);
		}

		write_speed(throttle_out, signal_out);
		move_stepper(stepper, target_bearing);

		read_from_arduinos(i2c0, i2c1, &real_speed, &real_bearing);
		send_update(sock, real_speed, real_bearing);
	}

    // Close pins
    mraa_gpio_close(dpdt_pin);
	mraa_gpio_close(manual_switch);
	mraa_aio_close(throttle_in);

	mraa_pwm_write(throttle_out, 0);
	mraa_pwm_close(throttle_out);

    mraa_i2c_stop(i2c0);
    mraa_i2c_stop(i2c1);

	close_stepper(stepper);

    return 0;
}
