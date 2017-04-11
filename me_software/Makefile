.SUFFIXES:

all: elecComms encoder dpdt throttle main i2c PID

elecComms: elecComms.c elecComms.h
	gcc -l mraa -c elecComms.c

encoder: encoder_driving.c
	gcc encoder_driving.c -l mraa -o encoder

dpdt: dpdt.c dpdt.h
	gcc -l mraa -c dpdt.c

throttle: throttle_control.c throttle_control.h
	gcc -l mraa -c throttle_control.c

i2c: i2c.c i2c.h
	gcc -l mraa -c i2c.c

stepper: Stepper-simple.c
	gcc Stepper-simple.c -l phidget21 -o stepper

PID: PID.c
	gcc PID.c -o pid

main: main.c dpdt elecComms throttle i2c
	gcc main.c dpdt.o i2c.o throttle_control.o elecComms.o -l mraa -o main

clean:
	$(RM) elecComms.o encoder dpdt.o throttle_control.o i2c.o stepper main

.phony: all clean
