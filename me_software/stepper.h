#ifndef STEPPER_H
#define STEPPER_H

#include <stdio.h>
#include <phidget21.h>

CPhidgetStepperHandle setup_stepper();

int move_stepper(CPhidgetStepperHandle stepper, float angle);

void close_stepper(CPhidgetStepperHandle stepper);

#endif
