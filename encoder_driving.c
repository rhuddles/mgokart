#include <mraa/gpio.h>
#include <time.h>

const int encoderA = 3;
const int encoderB = 2;

#define DELTA_TIME 100000 // 40 us = 25 kHz
#define COUNTS_PER_REV 20 // (48 counts/rev) * (9.7:1 gear ratio)

const int SPEED_INTERRUPT_PIN_A = 0
const int SPEED_INTERRUPT_PIN_B = 1

mraa_gpio_context speed_encoder_a;
mraa_gpio_context speed_encoder_b;

volatile int encoder = 0;

int oldPos = 0;

//float throttle = 0;

//int T = 50;

// TODO: make microseconds
clock_t start_time;
clock_t last_time;

void edison_isrA();
void edison_isrB();
int clock_to_ms(clock_t diff);

int main()
{
	speed_encoder_a = mraa_gpio_init(SPEED_INTERRUPT_PIN_A);
	speed_encoder_b = mraa_gpio_init(SPEED_INTERRUPT_PIN_B);

	// set pin direction to input
	mraa_gpio_dir(speed_encoder_a, MRAA_GPIO_IN);
	mraa_gpio_dir(speed_encoder_b, MRAA_GPIO_IN);

	// register interrupts
	mraa_gpio_isr(speed_encoder_a, MRAA_GPIO_EDGE_RISING, &edison_isrA);
	mraa_gpio_isr(speed_encoder_b, MRAA_GPIO_EDGE_RISING, &edison_isrB);

	last_time = clock();
	startTime = last_time;

	while (true) {
		int newPos = encoder;
		clock_t newTime = clock();
		clock_t period = clock_to_ms(newTime - timer);
		float omega = (newPos - oldPos)*1000*.15/(((float)period)*COUNTS_PER_REV)*60;

		oldPos = newPos;
		timer = newTime;

		printf("Omega: %f\n", omega);

		delay(20);
	}

	mraa_gpio_close(speed_encoder_a);
	mraa_gpio_close(speed_encoder_b);
	return 0;
}

void edison_isrA()
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

void edison_isrB()
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

int clock_to_ms(clock_t diff)
{
	return diff * 1000 / CLOCKS_PER_SEC;
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
