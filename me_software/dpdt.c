#include <mraa/gpio.h>

const int DPDT_PIN = 3;

mraa_gpio_context dpdt_pin;

int main(int argc, char **argv)
{
	int val = 0;
	if (argc > 1) {
		val = atoi(argv[1]);	
	}

	fprintf(stderr, "Writing %d to pin %d\n", val, DPDT_PIN);

	dpdt_pin = mraa_gpio_init(DPDT_PIN);
	mraa_gpio_dir(dpdt_pin, MRAA_GPIO_OUT);
	
	mraa_gpio_write(dpdt_pin, val);
}
