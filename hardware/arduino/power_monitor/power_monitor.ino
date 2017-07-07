
//constants for voltage divider measurement.
const float R1 = 1000000.0;
const float R2 = 100000.0;
const float VREF = 5.0;
float readVoltage;
float measuredVoltage;
float current;

//eqn for current across output pins: 
//I = (V*(1k ohm))/(R_s * R_l) where R_s = shunt resistor value and r_l = load resistor value
//however, on default board, R_s = 0.1 ohm and R_l = 10k, so all the resistors cancel out
//I = the voltage reading on the board

//notes (from SparkFun tutorial)
//make sure ground of measurement circuit is connected to ground of INA169 board. 

const int A_PIN = A1;
const int V_PIN = A0;

void setup() {
  Serial.begin(9600);
}

float readingToVoltage(float reading){
  return (reading*VREF)/1023;
}

float voltageDivider(float input){
  return (input)*(R1 + R2)/R2;
}

void loop() {
  // put your main code here, to run repeatedly:

  current = readingToVoltage(analogRead(A_PIN));
  Serial.print("Current: ");
  Serial.print(current, 3);
  Serial.print(" A ");

  measuredVoltage = voltageDivider(readingToVoltage(analogRead(V_PIN)));
  Serial.print("Voltage: ");
  Serial.print(measuredVoltage, 3);
  Serial.println(" V");

  
  

  delay(1000);

}
