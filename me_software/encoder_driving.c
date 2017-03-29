#include <mraa/gpio.h>
#include <unistd.h>
#include <math.h>

#define GEAR_RATIO (8.0 / 52.0)
#define WHEEL_RADIUS .15
#define WHEEL_CIRCUMFERENCE (2.0 * M_PI * WHEEL_RADIUS)

const double COUNTS_PER_REV = 20.0;

// Steering Wheel Pins
//const int SPEED_INTERRUPT_PIN_A = 4;
//const int SPEED_INTERRUPT_PIN_B = 6;

// Wheel Speed Pins
const int SPEED_INTERRUPT_PIN_A = 7;
const int SPEED_INTERRUPT_PIN_B = 8;

mraa_gpio_context speed_encoder_a;
mraa_gpio_context speed_encoder_b;

volatile long encoder = 0;
volatile long old_pos = 0;

struct timespec new_time, last_time;

void edison_isrA(void *);
void edison_isrB(void *);

int main()
{
	speed_encoder_a = mraa_gpio_init(SPEED_INTERRUPT_PIN_A);
	speed_encoder_b = mraa_gpio_init(SPEED_INTERRUPT_PIN_B);

	// set pin direction to input
	mraa_gpio_dir(speed_encoder_a, MRAA_GPIO_IN);
	mraa_gpio_dir(speed_encoder_b, MRAA_GPIO_IN);

	// register interrupts
	mraa_gpio_isr(speed_encoder_a, MRAA_GPIO_EDGE_BOTH, &edison_isrA, NULL);
	//mraa_gpio_isr(speed_encoder_b, MRAA_GPIO_EDGE_BOTH, &edison_isrB, NULL);

	clock_gettime(CLOCK_MONOTONIC, &last_time);

	FILE *output_file = fopen("output", "w");

	while (1) {
		long count_delta = encoder - old_pos;
		fprintf(output_file, "Old count: %ld\n", old_pos);
		fprintf(output_file, "Count: %ld\n", encoder);
		fprintf(output_file, "Delta Count: %ld\n", count_delta);

		clock_gettime(CLOCK_MONOTONIC, &new_time);
		double period = (new_time.tv_sec - last_time.tv_sec) +
			(new_time.tv_nsec - last_time.tv_nsec) / 1000000000.0; // seconds
		fprintf(output_file, "Period: %f\n", period);

		double omega = (count_delta * WHEEL_CIRCUMFERENCE * GEAR_RATIO) / (period * COUNTS_PER_REV);

		old_pos = encoder;
		last_time = new_time;

		fprintf(output_file, "%f m/s\n\n", omega);

		usleep(100000);
	}

	mraa_gpio_close(speed_encoder_a);
	mraa_gpio_close(speed_encoder_b);

	return MRAA_SUCCESS;
}

void edison_isrA(void *params)
{
	// Debouncing
	static int8_t encoder_states[] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
	static uint8_t old_AB = 0;

	int channelA = mraa_gpio_read(speed_encoder_a);
	int channelB = mraa_gpio_read(speed_encoder_b);

	old_AB <<= 2;
	old_AB |= (channelA & 0x1) << 1;
	old_AB |= (channelB & 0x1);

	if (encoder_states[old_AB & 0xf] != 0) {
		encoder++;
	}

	//if (channelA == channelB) {
	//	// encoder values are the same->positive rotation
	//	encoder--;
	//}
	//else {
	//	// encoder values are different->negative rotation
	//	encoder++;
	//}
}

void edison_isrB(void *params)
{
	int channelA = mraa_gpio_read(speed_encoder_a);
	int channelB = mraa_gpio_read(speed_encoder_b);

	if (channelA == channelB) {
		// encoder values are the same->positive rotation
		encoder++;
	}
	else {
		// encoder values are different->negative rotation
		encoder--;
	}
}

//void setup() {
//  // put your setup code here, to run once:
//
//  Serial.begin(115200);
//
//  // Declare Interrupt
//  attachInterrupt(1, isrA, CHANGE);
//  attachInterrupt(0, isrB, CHANGE);
//
//  // Declare Timer Interrupts
//  //Timer1.initialize(DELTA_TIME);
//  //Timer1.attachInterrupt(speedCalc);
//
////  Serial.print("Period = "); Serial.println(T);
//  Serial.println("Start:");
////  delay(5000);
////  Timer1.detachInterrupt();
////  Timer1.stop();
////  Serial.println("End");
//
//  timer = millis();
//  startTime = timer;
//}
//
//void isrA() {
//  int channelA = digitalRead(encoderA);
//  int channelB = digitalRead(encoderB);
//
//
//  if (channelA == channelB) { // encoder values are the same->positive rotation
//    encoder--;
//  }
//
//  else {  // encoder values are different->negative rotation
//    encoder++;
//  }
//
//  //reportEncoderData(channelA, channelB);
//  //speedCalc();
//}
//
//void isrB() {
//  int channelA = digitalRead(encoderA);
//  int channelB = digitalRead(encoderB);
//
//
//  if (channelA == channelB) { // encoder values are the same->positive rotation
//    encoder++;
//  }
//
//  else {  // encoder values are different->negative rotation
//    encoder--;
//  }
//
//  //reportEncoderData(channelA, channelB);
//  //speedCalc();
//}
//
//void reportEncoderData(int channelA, int channelB) {
//  Serial.print(channelA);
//  Serial.print('\t');
//  Serial.print(channelB);
//  Serial.print('\t');
//  Serial.println(encoder);
//}
//
//void loop() {
////  //This makes a sine wave - don't worry about it
////  throttle = sin(2*3.14*timer/T) * 100;
////  throttle = map(throttle, -100, 100, 255*.9/5, 255*3.5/5);
////  analogWrite(9, throttle);
//
//  int newPos = encoder;
//  unsigned long newTime = millis();
//  unsigned long period = newTime - timer;
//  float omega = (newPos - oldPos)*1000*.15/(((float)period)*COUNTS_PER_REV)*60;
//
//  oldPos = newPos;
//  timer = newTime;
//
////  Serial.print(throttle);
////  Serial.print('\t');
//  Serial.println(omega);
//
//  delay(20);
//
////  //This was meant to end the sample time - ignore
////  if ( (millis()- startTime) > 10000 ) {
////    analogWrite(9, 0);
////    Serial.println("End");
////    delay(1000000000);
////  }
//}
//
