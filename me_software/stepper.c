// - Stepper simple -
// This simple example sets up a Stepper object, hooks the event handlers and opens it for device connections.
// Once an Advanced Servo is attached it will move the motor to various positions.
//
// Please note that this example was designed to work with only one Phidget Stepper connected.
//
// Copyright 2008 Phidgets Inc.  All rights reserved.
// This work is licensed under the Creative Commons Attribution 2.5 Canada License.
// view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/

//#include <unistd.h>

#include "stepper.h"

CPhidgetStepperHandle setup_stepper()
{
	int result;
	const char* err;

	//Declare an stepper handle
	CPhidgetStepperHandle stepper = 0;

	//create the stepper object
	CPhidgetStepper_create(&stepper);

	//open the device for connections
	CPhidget_open((CPhidgetHandle)stepper, -1);

	//get the program to wait for an stepper device to be attached
	if((result = CPhidget_waitForAttachment((CPhidgetHandle)stepper, 10000)))
	{
		CPhidget_getErrorDescription(result, &err);
		printf("Problem waiting for attachment: %s\n", err);
		return 0;
	}

	//TODO: Figure out the best values for these
	//Set up some initial acceleration and velocity values
	CPhidgetStepper_setAcceleration(stepper, 0, 12500);
	CPhidgetStepper_setVelocityLimit(stepper, 0, 100000);

	CPhidgetStepper_setCurrentPosition(stepper, 0, 0);
	CPhidgetStepper_setEngaged(stepper, 0, 1);

	return stepper;
}

int move_stepper(CPhidgetStepperHandle stepper, float angle)
{
	int count = (angle * (51.0 * 3.0)) / .035;
	CPhidgetStepper_setTargetPosition (stepper, 0, count);

	return 0;
}

void close_stepper(CPhidgetStepperHandle stepper)
{
	CPhidgetStepper_setEngaged(stepper, 0, 0);

	CPhidget_close((CPhidgetHandle)stepper);
	CPhidget_delete((CPhidgetHandle)stepper);
}

