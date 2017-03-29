all: elecComms encoder dpdt throttle

elecComms: elecComms.cpp
	g++ elecComms.cpp --std=c++11 -lpthread -lmraa -o elecComms

encoder: encoder_driving.c
	gcc encoder_driving.c -l mraa -o encoder

dpdt: dpdt.c
	gcc dpdt.c -l mraa -o dpdt

throttle: throttle_signal.c
	gcc throttle_signal.c -l mraa -o throttle

clean:
	$(RM) elecComms encoder dpdt throttle

.phony: all clean
