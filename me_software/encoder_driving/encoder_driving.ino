const int encoderA = 3;
const int encoderB = 2;

const int interruptA = 1;
const int interruptB = 0;

volatile int encoder = 0;

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

void setup() {
  Serial.begin(115200);

  attachInterrupt(interruptA, isrA, CHANGE);
  attachInterrupt(interruptB, isrB, CHANGE);
}

void loop() {
  char toSend[MSG_LEN] = {0};
  String encoderStr(encoder);
  encoderStr.toCharArray(toSend, MSG_LEN);
  Serial.write((uint8_t*)toSend, MSG_LEN);

  delay(20); // 20 milliseconds
}

