#include <Wire.h>

#define portOfPin(P)\
  (((P)>=0&&(P)<8)?&PORTD:(((P)>7&&(P)<14)?&PORTB:&PORTC))
#define ddrOfPin(P)\
  (((P)>=0&&(P)<8)?&DDRD:(((P)>7&&(P)<14)?&DDRB:&DDRC))
#define pinOfPin(P)\
  (((P)>=0&&(P)<8)?&PIND:(((P)>7&&(P)<14)?&PINB:&PINC))
#define pinIndex(P)((uint8_t)(P>13?P-14:P&7))
#define pinMask(P)((uint8_t)(1<<pinIndex(P)))

#define pinAsInput(P) *(ddrOfPin(P))&=~pinMask(P)
#define pinAsInputPullUp(P) *(ddrOfPin(P))&=~pinMask(P);digitalHigh(P)
#define pinAsOutput(P) *(ddrOfPin(P))|=pinMask(P)
#define digitalLow(P) *(portOfPin(P))&=~pinMask(P)
#define digitalHigh(P) *(portOfPin(P))|=pinMask(P)
#define isHigh(P)((*(pinOfPin(P))& pinMask(P))>0)
#define isLow(P)((*(pinOfPin(P))& pinMask(P))==0)
#define digitalState(P)((uint8_t)isHigh(P))

unsigned long timer;
const int encoderA = 3;
const int encoderB = 2;
const int LED = 6;

#define DELTA_TIME 100000 // 40 us = 25 kHz
#define COUNTS_PER_REV 20.0 // (48 counts/rev) * (9.7:1 gear ratio)
#define MSG_LEN 6

volatile unsigned long encoder = 0;

unsigned long oldPos = 0;

float throttle = 0;

int T = 1000;
unsigned long startTime;

void setup() {
  // put your setup code here, to run once:
  pinMode(9, OUTPUT);
  pinMode(encoderA, INPUT);
  pinMode(encoderB, INPUT);

  // Declare Interrupt
  attachInterrupt(1, isrA, CHANGE);
  attachInterrupt(0, isrB, CHANGE);
  
  // Setup I2C
  Wire.begin(2);
  Wire.onRequest(requestEvent);
}

void isrA() {
  int channelA = isHigh(encoderA);
  int channelB = isHigh(encoderB);
  

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
  int channelA = isHigh(encoderA);
  int channelB = isHigh(encoderB);

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
  
//  throttle = sin(2*3.14*timer/T) * 100;
//  throttle = map(throttle, -100, 100, 255*.9/5, 255*3.5/5);
//  analogWrite(9, throttle);
  
//  unsigned long long newPos = encoder;
//  unsigned long newTime = millis();
//  unsigned long period = newTime - timer;
//  float omega = (newPos - oldPos)*1000.0*2.0*3.14*(8.0/52.0)*0.15/(((float)period)*COUNTS_PER_REV);
//  
//  oldPos = newPos;
//  timer = newTime;

//  Serial.print(throttle);
//  Serial.print('\t');
//  Serial.println(omega);

  delay(150);

//  if ( (millis()- startTime) > 1000 ) {
//    analogWrite(9, 0);
//    Serial.println("End");
//    Serial.println(encoder);
//    delay(100000000);
//  }
}

void requestEvent()
{                       
  char toSend[MSG_LEN] = {0};
  String encoderStr(encoder - oldPos);
  encoderStr.toCharArray(toSend, MSG_LEN);
  Wire.write((uint8_t*)toSend, MSG_LEN);
  oldPos = encoder;
}

