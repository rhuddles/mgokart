.SUFFIXES:

all: elecComms encoder dpdt throttle main i2c

elecComms: elecComms.cpp
	g++ elecComms.cpp --std=c++11 -lpthread -lmraa -o elecComms

encoder: encoder_driving.c
	gcc encoder_driving.c -l mraa -o encoder

dpdt: dpdt.c dpdt.h
	gcc -c dpdt.c -l mraa

throttle: dpdt throttle_control.c
	gcc throttle_control.c dpdt.o -l mraa -o throttle

i2c: i2c.c
	gcc i2c.c -l mraa -o i2c

stepper: Stepper-simple.c
	gcc Stepper-simple.c -l phidget21 -o stepper

main: main.c dpdt
	gcc main.c dpdt.o -l mraa -o main

clean:
	$(RM) elecComms encoder dpdt.o throttle i2c stepper main

.phony: all clean
