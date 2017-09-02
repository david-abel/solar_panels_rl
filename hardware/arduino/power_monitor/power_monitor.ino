
//constants for voltage divider measurement.
//const float R1 = 1000000.0;
//const float R2 = 100000.0;
//const float R1 = 1010000.0;
//const float R2 = 99700.0;

const float R1 = 1023000.0;
const float R2 = 99500.0;
const float VREF = 3.33; //V, technically only valid if using external power source, USB power is ~4.83
float readVoltage; //V``
float measuredVoltage; //V
float current; //A
float power; //W

//use serial plotter or serial monitor
//plotter is kind of useless b/c different units, tbh
//maybe use Simulink or something
bool usePlotter = false;

//eqn for current across output pins: 
//I = (V*(1k ohm))/(R_s * R_l) where R_s = shunt resistor value and r_l = load resistor value
//however, on default board, R_s = 0.1 ohm and R_l = 10k, so all the resistors cancel out
//I = the voltage reading on the board

//notes (from SparkFun tutorial)
//make sure ground of measurement circuit is connected to ground of INA169 board. 
////For solar panel
//const int A_PIN = A3;
//const int V_PIN = A2;

const int A_PIN = A1;
const int V_PIN = A0;

void setup() {
  Serial.begin(9600);
  analogReference(EXTERNAL);
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

  //using Serial plotter

//  Serial.print(current, 3);
//  if (!usePlotter){
//    Serial.print(" A ");
//  } else{
//    Serial.print("\t"); 
//  }
//  
  

  measuredVoltage = voltageDivider(readingToVoltage(analogRead(V_PIN)));
//  measuredVoltage = readingToVoltage(analogRead(V_PIN));
  
  Serial.print(measuredVoltage, 3);

  if (!usePlotter){
    Serial.print(" V ");
  } else{
    Serial.print("\t"); 
  }
  
  
  

  power = current*measuredVoltage;

  Serial.print(power);

  if (!usePlotter){
    Serial.println(" W");
  } else{
    Serial.println("");
  }
  
  

  delay(1000);

}
