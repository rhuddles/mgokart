unsigned long timer;
const int encoderA = 3;
const int encoderB = 2;

#define DELTA_TIME 100000 // 40 us = 25 kHz
#define COUNTS_PER_REV 20 // (48 counts/rev) * (9.7:1 gear ratio)

volatile int encoder = 0;

int oldPos = 0;

//float throttle = 0;

//int T = 50;
unsigned long startTime;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);

  // Declare Interrupt
  attachInterrupt(1, isrA, CHANGE);
  attachInterrupt(0, isrB, CHANGE);

  // Declare Timer Interrupts
  //Timer1.initialize(DELTA_TIME);
  //Timer1.attachInterrupt(speedCalc);
  
//  Serial.print("Period = "); Serial.println(T);
  Serial.println("Start:");
//  delay(5000);
//  Timer1.detachInterrupt();
//  Timer1.stop();
//  Serial.println("End");

  timer = millis();
  startTime = timer;
}

void isrA() {
  int channelA = digitalRead(encoderA);
  int channelB = digitalRead(encoderB);
  

  if (channelA == channelB) { // encoder values are the same->positive rotation
    encoder--;
  }

  else {  // encoder values are different->negative rotation
    encoder++;
  }

  //reportEncoderData(channelA, channelB);
  //speedCalc();
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

  //reportEncoderData(channelA, channelB);
  //speedCalc();
}

void reportEncoderData(int channelA, int channelB) {
  Serial.print(channelA);
  Serial.print('\t');
  Serial.print(channelB);
  Serial.print('\t');
  Serial.println(encoder);
}

void loop() {
//  //This makes a sine wave - don't worry about it
//  throttle = sin(2*3.14*timer/T) * 100;
//  throttle = map(throttle, -100, 100, 255*.9/5, 255*3.5/5);
//  analogWrite(9, throttle);
  
  int newPos = encoder;
  unsigned long newTime = millis();
  unsigned long period = newTime - timer;
  float omega = (newPos - oldPos)*1000*.15/(((float)period)*COUNTS_PER_REV)*60;
  
  oldPos = newPos;
  timer = newTime;

//  Serial.print(throttle);
//  Serial.print('\t');
  Serial.println(omega);

  delay(20);

//  //This was meant to end the sample time - ignore
//  if ( (millis()- startTime) > 10000 ) {
//    analogWrite(9, 0);
//    Serial.println("End");
//    delay(1000000000);
//  }
}

