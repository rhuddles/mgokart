.SUFFIXES:

all: main PID

elecComms: elecComms.c elecComms.h
	g++ -lmraa -c elecComms.c

encoder: encoder_driving.c
	gcc encoder_driving.c -l mraa -o encoder

dpdt: dpdt.c dpdt.h
	g++ -lmraa -c dpdt.c

throttle: throttle_control.c throttle_control.h
	g++ -lmraa -c throttle_control.c

i2c: i2c.c i2c.h
	g++ -lmraa -c i2c.c

stepper: stepper.c stepper.h
	g++ -lphidget21 -c stepper.c

PID: PID.c
	gcc PID.c -o pid

main: main.cpp dpdt elecComms throttle i2c stepper
	g++ main.cpp dpdt.o i2c.o throttle_control.o elecComms.o stepper.o -lpthread -lmraa -lphidget21 --std=c++11 -o main

clean:
	$(RM) encoder *.o pid main

.phony: all clean
