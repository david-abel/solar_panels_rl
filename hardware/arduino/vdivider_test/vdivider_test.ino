//voltage measurement via voltage divider. 


float R1 = 1000000.0;
float R2 = 100000.0;
const int V_PIN = A0;

float VREF = 5.0;
float readVoltage;
float measuredVoltage;

void setup() {

  Serial.begin(9600);
}

void loop() {

  readVoltage = (analogRead(V_PIN)*VREF)/1023;

  //Serial.println(readVoltage);
  measuredVoltage = (readVoltage)*(R1 + R2)/R2;
  Serial.println(measuredVoltage);
  //observed difference between multimeter and reality - errors probably ADC error at low analog voltages

  delay(500);

}
