#include <mraa/gpio.h>
#include <unistd.h>

#define DELTA_TIME 100000 // 40 us = 25 kHz
#define COUNTS_PER_REV 20.0 // (48 counts/rev) * (9.7:1 gear ratio)

// Steering Wheel
//const int SPEED_INTERRUPT_PIN_A = 4;
//const int SPEED_INTERRUPT_PIN_B = 6;

const int SPEED_INTERRUPT_PIN_A = 7;
const int SPEED_INTERRUPT_PIN_B = 8;

mraa_gpio_context speed_encoder_a;
mraa_gpio_context speed_encoder_b;

volatile int encoder = 0;

int oldPos = 0;

//float throttle = 0;

//int T = 50;

// TODO: make microseconds
time_t last_time;

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
	mraa_gpio_isr(speed_encoder_b, MRAA_GPIO_EDGE_BOTH, &edison_isrB, NULL);

	last_time = time(NULL);

	while (1) {
		//printf("Encoder: %d\n", encoder);
		int newPos = encoder;
		time_t newTime = time(NULL);
		float period = (float)difftime(newTime, last_time);
		float omega = (((float)(newPos - oldPos)) * .15 * 2.0 * 3.14)/(period * COUNTS_PER_REV);

		oldPos = newPos;
		last_time = newTime;

		printf("%f m/s\n", omega);

		usleep(100000);
	}

	mraa_gpio_close(speed_encoder_a);
	mraa_gpio_close(speed_encoder_b);
	return 0;
}

void edison_isrA(void *params)
{
	int channelA = mraa_gpio_read(speed_encoder_a);
	int channelB = mraa_gpio_read(speed_encoder_b);

	if (channelA == channelB) {
		// encoder values are the same->positive rotation
		encoder--;
	}
	else {
		// encoder values are different->negative rotation
		encoder++;
	}
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
