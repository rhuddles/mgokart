#define GEAR_RATIO (8.0 / 52.0)
#define WHEEL_RADIUS (.15)
#define WHEEL_CIRCUMFERENCE (2.0 * M_PI * WHEEL_RADIUS)
#define COUNTS_PER_REV (20.0)

const int encoderA = 3;
const int encoderB = 2;

const int interruptA = 1;
const int interruptB = 0;

volatile long encoder = 0;
volatile long old_pos = 0;

unsigned long last_time;
  
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

void setup() {
  Serial.begin(115200);

  attachInterrupt(interruptA, isrA, CHANGE);
  attachInterrupt(interruptB, isrB, CHANGE);

  last_time = millis();
}

void loop() {
  long count_delta = encoder - old_pos;

  unsigned long now = millis();
  unsigned long period = now - last_time;

  double spd = (count_delta * WHEEL_CIRCUMFERENCE * GEAR_RATIO * 1000)
                / (period * COUNTS_PER_REV);
  Serial.println(spd);

  old_pos = encoder;
  last_time = now;
  
  delay(20);
}

