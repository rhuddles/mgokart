.SUFFIXES:

all: main PID

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

stepper: stepper.c stepper.h
	gcc -l phidget21 -c stepper.c

PID: PID.c
	gcc PID.c -o pid

main: main.c dpdt elecComms throttle i2c stepper
	gcc main.c dpdt.o i2c.o throttle_control.o elecComms.o stepper.o -l mraa -l phidget21 -o main

clean:
	$(RM) encoder *.o main

.phony: all clean
