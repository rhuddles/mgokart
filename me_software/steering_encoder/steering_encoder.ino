#include <Wire.h>

#define I2C_BUS_ADDRESS 3
#define MESSAGE_LEN 10

const int encoderA = 3;
const int encoderB = 2;

const int interruptA = 1;
const int interruptB = 0;

volatile long encoder = 0;

const int MSG_LEN = 6;

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

double countToDegrees(int count) {
  const double STEP_ANGLE = .035; // From datasheet
  return ((double)count * STEP_ANGLE) / (51.0 * 3.0);
}

void dataRequested() {
  Serial.println(encoder);
  String message = String(encoder);
  char cstr[MESSAGE_LEN] = {0};
  message.toCharArray(cstr, MESSAGE_LEN);
  Wire.write((uint8_t*)cstr, MESSAGE_LEN);
}

void setup() {
  Wire.begin(I2C_BUS_ADDRESS);
  Wire.onRequest(dataRequested);

  Serial.begin(115200);

  attachInterrupt(interruptA, isrA, CHANGE);
  attachInterrupt(interruptB, isrB, CHANGE);
}

void loop() {
  // lol
  while (true) {}
}

