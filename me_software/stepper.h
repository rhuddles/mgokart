#ifndef STEPPER_H
#define STEPPER_H

#include <phidget21.h>
#include <stdio.h>

extern "C" CPhidgetStepperHandle setup_stepper();

extern "C" int move_stepper(CPhidgetStepperHandle stepper, float angle);

extern "C" void close_stepper(CPhidgetStepperHandle stepper);

#endif
