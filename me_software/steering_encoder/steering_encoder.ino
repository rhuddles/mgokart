#include <Wire.h>

#define I2C_BUS_ADDRESS 3
#define MESSAGE_LEN 10

const int encoderA = 1;
const int encoderB = 0;

const int interruptA = 3;
const int interruptB = 2;

volatile long encoder = 0;
double angle = 0;
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
  const double STEP_ANGLE = (.035*16/2.2); // From datasheet
  return ((double)count * STEP_ANGLE) / (50.894897 * 2.916666666666666666666666667);
}

void dataRequested() {
  String message = String(angle);
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
  angle=countToDegrees(encoder);
  Serial.println(angle);
  delay(200);
}

