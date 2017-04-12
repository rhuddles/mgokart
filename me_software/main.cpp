#include "dpdt.h"
#include "elecComms.h"
#include "i2c.h"
#include "stepper.h"
#include "throttle_control.h"

#include <mutex>
#include <thread>

#define DEFAULT_PORT 8090

class Setpt_t
{
public:
	Setpt_t() : speed(0), bearing(0)
	{}

	void set(double target_speed, double target_bearing)
	{
		std::lock_guard<std::mutex> l(m);
		speed = target_speed;
		bearing = target_bearing;
	}

	std::pair<double, double> get()
	{
		std::lock_guard<std::mutex> l(m);
		return {speed, bearing};
	}

private:
	std::mutex m;
	double speed, bearing;
};

int running = 1;
Setpt_t setpt;

/**
 * For testing all the modules
 */

void stop_running(int signal)
{
	running = 0;
}

void get_setpts(int sock)
{
	double target_speed = 0, target_bearing = 0;

	while (running)
	{
		// edits speed and bearing to be the targets
		get_commands(sock, &target_speed, &target_bearing);

		setpt.set(target_speed, target_bearing);
	}
}

void get_speed_bearing(int sock)
{
	double real_speed = 0, real_bearing = 0;

	fprintf(stderr, "Initializing I2C\n");
	// Init I2C
    mraa_i2c_context i2c0 = mraa_i2c_init(0); // Set as master
    mraa_i2c_context i2c1 = mraa_i2c_init(0); // Set as master
    mraa_i2c_address(i2c0, I2C_ADDRESS0);
    mraa_i2c_address(i2c1, I2C_ADDRESS1);

	while (running)
	{
		//read_from_arduino(i2c0, &real_speed);
		real_speed = 0;
		//usleep(1000000);
		read_from_arduino(i2c1, &real_bearing);
		fprintf(stderr, "Real Speed: %f\tReal Bearing: %f\n", real_speed, real_bearing);
		//send_update(sock, real_speed, real_bearing);
		usleep(100000);
	}

	//Close pins
    mraa_i2c_stop(i2c0);
    mraa_i2c_stop(i2c1);
}

void actuate(void)
{
	int autonomous;
	float signal_out, volt_out, target_bearing;
	std::pair<double, double> target = {0, 0};

	fprintf(stderr, "Initializing DPDT\n");
    // Init DPDT
    mraa_gpio_context dpdt_pin = init_dpdt();

	fprintf(stderr, "Initializing Manual Switch\n");
	// Init GPIO
	mraa_gpio_context manual_switch = mraa_gpio_init(MANUAL_SWITCH_PIN);
	mraa_gpio_dir(manual_switch, MRAA_GPIO_IN);

	fprintf(stderr, "Initializing Throttle In\n");
	// Init Analog
	mraa_aio_context throttle_in = mraa_aio_init(THROTTLE_SIGNAL_ANA);

	fprintf(stderr, "Initializing Throttle Out\n");
	// Init PWM
	mraa_pwm_context throttle_out = mraa_pwm_init(THROTTLE_SIGNAL_PWM);
	mraa_pwm_period_us(throttle_out, 50);
	mraa_pwm_enable(throttle_out, 1);

	fprintf(stderr, "Initializing Stepper\n");
	// Init Stepper Motor
	CPhidgetStepperHandle stepper = setup_stepper();

	fprintf(stderr, "Writing 0 to DPDT\n");
    // Set DPDT to reverse then forward
    mraa_gpio_write(dpdt_pin, DPDT_FORWARD);

	while (running)
	{
		// Check if manual or autonomous
		autonomous = mraa_gpio_read(manual_switch);
		if (autonomous) {
			target = setpt.get();

			volt_out = (target.first + 4.587) / 4.483;
			signal_out = volt_out / REFERENCE_VOLTAGE;
			target_bearing = target.second;
		}
		else {
		    signal_out = read_analog_signal(throttle_in);
			target_bearing = 0;
		}

		write_speed(throttle_out, signal_out);
		move_stepper(stepper, target_bearing);
	}

    // Close pins
    mraa_gpio_close(dpdt_pin);
	mraa_gpio_close(manual_switch);
	mraa_aio_close(throttle_in);

	mraa_pwm_write(throttle_out, 0);
	mraa_pwm_close(throttle_out);

	close_stepper(stepper);
}

int main(void)
{
	int sock = 0;

	signal(SIGINT, stop_running);
	signal(SIGABRT, stop_running);

	fprintf(stderr, "Waiting for socket connection\n");
	sock = open_socket(DEFAULT_PORT);
	if (sock == -1)
	{
		fprintf(stderr, "Error: could not open socket\n");
		return 1;
	}
	fprintf(stderr, "Connected to socket\n");

	std::thread t1(get_setpts, sock);
	std::thread t2(get_speed_bearing, sock);
	std::thread t3(actuate);

	t1.join();
	t2.join();

    return 0;
}
