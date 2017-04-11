#include <Wire.h>

#define I2C_BUS_ADDRESS 2
#define MESSAGE_LEN 10

//#define OUTPUT_PIN 9

#define GEAR_RATIO (8.0 / 52.0)
#define WHEEL_RADIUS (.15)
#define WHEEL_CIRCUMFERENCE (2.0 * M_PI * WHEEL_RADIUS)
#define COUNTS_PER_REV (20.0)

const int encoderA = 1;
const int encoderB = 0;

const int interruptA = 3;
const int interruptB = 2;

volatile long encoder = 0;
volatile long old_pos = 0;

unsigned long start_time;
unsigned long last_time;

volatile double current_speed = 0;

void isrA() {
  int channelA = digitalRead(encoderA);
  int channelB = digitalRead(encoderB);

  if (channelA == channelB) { // encoder values are the same->positive rotation
    encoder--;
  }

  else {  // encoder values are different->negative rotation
    encoder++;
  }
}

void isrB() {
  int channelA = digitalRead(encoderA);
  int channelB = digitalRead(encoderB);

  if (channelA == channelB) { // encoder values are the same->positive rotation
    encoder++;
  }

  else {  // encoder values are different->negative rotation
    encoder--;
  }
}

void dataRequested() {
  String message = String(current_speed);
  char cstr[MESSAGE_LEN] = {0};
  message.toCharArray(cstr, MESSAGE_LEN);

  Wire.write(cstr, MESSAGE_LEN);
}

void setup() {
  Wire.begin(I2C_BUS_ADDRESS);
  Wire.onRequest(dataRequested);

  Serial.begin(115200);

  attachInterrupt(interruptA, isrA, CHANGE);
  attachInterrupt(interruptB, isrB, CHANGE);

//  analogWrite(OUTPUT_PIN, 102);

  last_time = millis();
}

void loop() {
  long count_delta = encoder - old_pos;

  unsigned long now = millis();
  unsigned long period = now - last_time;

  current_speed = (count_delta * WHEEL_CIRCUMFERENCE * GEAR_RATIO * 1000)
                / (period * COUNTS_PER_REV);

  Serial.print(current_speed);
  Serial.print("\t");
  Serial.print(count_delta);
  Serial.print("\t");
  Serial.print(period);
  Serial.print("\n");

  old_pos = encoder;
  last_time = now;

  delay(100);

//  if (millis() - start_time > 10000) {
//    analogWrite(OUTPUT_PIN, 0);
//    Serial.println("End");
//    delay(100000000);
//  }
}

