// #include <unistd.h>
#include <stdio.h>
#include <windows.h>
double new_accel = 0;
double new_speed = 0;
double time_step = 1; // In milliseconds

// Runs the transfer function. Turns a voltage into a speed
void transfer(double act_speed, double volt, double time_step, double act_accel) {
	new_speed = act_speed + time_step*act_accel + time_step*(0.86*(volt / time_step) + 0.53*volt);
	new_accel = -0.29*time_step*act_speed + (1-1.4*time_step)*act_accel + time_step*(0.86*(volt / time_step) + 0.53*volt);
}

// Takes the difference in speed and outputs a voltage
double PID(double desired_speed, double actual_speed, double iteration_time) {

		double error_prior = 0;
		double error = 0;
		double derivative = 0;
		double integral = 0;
		double bias = 0;
		double output_voltage = 0;
		int Kp = 1.2674;
		int Ki = 0.80143;
		int Kd = 0.047772;

		error = desired_speed - actual_speed;
		integral = integral + (error*iteration_time);
		derivative = (error - error_prior) / iteration_time;
		output_voltage = Kp*error + Ki*integral + Kd*derivative + bias;

		if (output_voltage > 3.5)
			output_voltage = 3.5;
		else if (output_voltage < 0 && output_voltage > -2)
			output_voltage = 0;
		else if (output_voltage < -3.5)
			output_voltage = -3.5;
		else
			output_voltage = output_voltage;

		error_prior = error;
		return output_voltage;
		

	}

int main(){
	double des_speed;
	double act_speed;
	double output_volt;
	double act_accel = 0;
printf("Input desired speed:");
scanf("%lf", &des_speed);
printf("Input actual speed:");
scanf("%lf", &act_speed);

double time = 0;
int steady_time = 0;
while (1) {
	
	output_volt = PID(des_speed, act_speed, time_step/1000);
	printf("Voltage: ");
	printf("%lf", output_volt);
	printf("                     ");
	transfer(act_speed, output_volt, time_step/1000, act_accel);
	printf("Speed: ");
	printf("%lf\n", new_speed);
	act_speed = new_speed;
	act_accel = new_accel;
	time++;
	if (steady_time == 500) {
		break;
	}
	
	if (des_speed < (act_speed + (act_speed*0.005)) && des_speed > act_speed - (act_speed*0.005)) {
		steady_time++;
		
	}
	Sleep(time_step);
	
	
}
printf("Settling time: ");
printf("%lf", time/1000);

return (0);
}
